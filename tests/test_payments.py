import pytest
from uuid import uuid4
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_invoice():
    """
    Create a customer, plan, subscription, and invoice.
    Returns the created invoice response.
    """
    unique_id = uuid4().hex

    # Create customer
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Payment Test Customer",
            "email": f"payment_{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201
    customer_id = customer_response.json()["id"]

    # Create plan
    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Payment Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "999.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201
    plan_id = plan_response.json()["id"]

    # Create subscription
    subscription_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert subscription_response.status_code == 201
    subscription_id = subscription_response.json()["id"]

    # Create invoice
    invoice_response = client.post(
        "/invoices/",
        json={
            "subscription_id": subscription_id,
        },
    )

    assert invoice_response.status_code == 201

    return invoice_response.json()


def create_payment(invoice_id, amount):
    return client.post(
        "/payments/",
        json={
            "invoice_id": invoice_id,
            "amount": str(amount),
        },
    )


def update_payment(payment_id, status, provider_reference=None,
                   failure_reason=None):
    return client.patch(
        f"/payments/{payment_id}",
        json={
            "status": status,
            "provider_reference": provider_reference,
            "failure_reason": failure_reason,
        },
    )


def test_create_payment_attempt():
    invoice = create_test_invoice()

    response = create_payment(
        invoice["id"],
        Decimal("999.00"),
    )

    assert response.status_code == 201

    payment = response.json()

    assert payment["invoice_id"] == invoice["id"]
    assert Decimal(payment["amount"]) == Decimal("999.00")
    assert payment["currency"] == "INR"
    assert payment["status"] == "pending"


def test_successful_payment_marks_invoice_paid():
    invoice = create_test_invoice()

    payment_response = create_payment(
        invoice["id"],
        Decimal("999.00"),
    )

    assert payment_response.status_code == 201

    payment_id = payment_response.json()["id"]

    # Mark payment as successful
    update_response = update_payment(
        payment_id,
        "succeeded",
        provider_reference=f"PAY-SUCCESS-{uuid4().hex}",
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "succeeded"

    # Verify invoice balance
    invoice_response = client.get(
        f"/invoices/{invoice['id']}"
    )

    assert invoice_response.status_code == 200

    updated_invoice = invoice_response.json()

    assert Decimal(updated_invoice["amount_paid"]) == Decimal("999.00")
    assert updated_invoice["status"] == "paid"

    # Verify ledger entry
    ledger_response = client.get(
        f"/ledger/invoice/{invoice['id']}"
    )

    assert ledger_response.status_code == 200

    ledger_entries = ledger_response.json()

    assert len(ledger_entries) == 2

    invoice_entry = next(
            entry
            for entry in ledger_entries
            if entry["entry_type"] == "invoice_created"
        )

    payment_entry = next(
            entry
            for entry in ledger_entries
            if entry["entry_type"] == "payment_success"
        )

    assert invoice_entry["invoice_id"] == invoice["id"]

    assert payment_entry["reference_id"] == payment_id
    assert payment_entry["entry_type"] == "payment_success"
    assert Decimal(payment_entry["amount"]) == Decimal("999.00")


def test_partial_payment_updates_invoice_balance():
    invoice = create_test_invoice()

    payment_response = create_payment(
        invoice["id"],
        Decimal("400.00"),
    )

    assert payment_response.status_code == 201

    payment_id = payment_response.json()["id"]

    update_response = update_payment(
        payment_id,
        "succeeded",
        provider_reference=f"PAY-PARTIAL-{uuid4().hex}",
    )

    assert update_response.status_code == 200

    invoice_response = client.get(
        f"/invoices/{invoice['id']}"
    )

    assert invoice_response.status_code == 200

    updated_invoice = invoice_response.json()

    assert Decimal(updated_invoice["amount_paid"]) == Decimal("400.00")
    assert updated_invoice["status"] == "partially_paid"


def test_failed_payment_does_not_update_invoice():
    invoice = create_test_invoice()

    payment_response = create_payment(
        invoice["id"],
        Decimal("999.00"),
    )

    assert payment_response.status_code == 201

    payment_id = payment_response.json()["id"]

    update_response = update_payment(
        payment_id,
        "failed",
        provider_reference=f"PAY-FAILED-{uuid4().hex}",
        failure_reason="Payment declined",
    )

    assert update_response.status_code == 200

    payment = update_response.json()

    assert payment["status"] == "failed"
    assert payment["failure_reason"] == "Payment declined"

    # Invoice must remain unpaid
    invoice_response = client.get(
        f"/invoices/{invoice['id']}"
    )

    assert invoice_response.status_code == 200

    updated_invoice = invoice_response.json()

    assert Decimal(updated_invoice["amount_paid"]) == Decimal("0.00")
    assert updated_invoice["status"] == "unpaid"

    # Failed payment must not create a ledger entry
    # Invoice creation and failed payment should both be recorded.
    ledger_response = client.get(
    f"/ledger/invoice/{invoice['id']}"
    )

    assert ledger_response.status_code == 200

    ledger_entries = ledger_response.json()

    assert len(ledger_entries) == 2

    entry_types = {
        entry["entry_type"]
        for entry in ledger_entries
    }

    assert "invoice_created" in entry_types
    assert "payment_failure" in entry_types

    failure_entry = next(
        entry
        for entry in ledger_entries
        if entry["entry_type"] == "payment_failure"
    )

    assert failure_entry["reference_id"] == payment_id
    assert Decimal(failure_entry["amount"]) == Decimal("999.00")



def test_payment_cannot_be_processed_twice():
    invoice = create_test_invoice()

    payment_response = create_payment(
        invoice["id"],
        Decimal("999.00"),
    )

    assert payment_response.status_code == 201

    payment_id = payment_response.json()["id"]
    provider_reference = f"PAY-DUPLICATE-{uuid4().hex}"

    # First successful update
    first_response = update_payment(
        payment_id,
        "succeeded",
        provider_reference=provider_reference,
    )

    assert first_response.status_code == 200

    # Second update must be rejected
    second_response = update_payment(
        payment_id,
        "succeeded",
        provider_reference=provider_reference,
    )

    assert second_response.status_code == 409

    # Invoice should not be paid twice
    invoice_response = client.get(
        f"/invoices/{invoice['id']}"
    )

    assert invoice_response.status_code == 200

    updated_invoice = invoice_response.json()

    assert Decimal(updated_invoice["amount_paid"]) == Decimal("999.00")
    assert updated_invoice["status"] == "paid"

    # Only one ledger entry should exist
    # Invoice creation and the successful payment should each
# produce one ledger entry. The duplicate request must not
# create another payment entry.
    ledger_response = client.get(
        f"/ledger/invoice/{invoice['id']}"
    )

    assert ledger_response.status_code == 200

    ledger_entries = ledger_response.json()

    assert len(ledger_entries) == 2

    payment_entries = [
        entry
        for entry in ledger_entries
        if entry["entry_type"] == "payment_success"
    ]

    assert len(payment_entries) == 1
    assert payment_entries[0]["reference_id"] == payment_id


def test_payment_cannot_exceed_outstanding_balance():
    invoice = create_test_invoice()

    response = create_payment(
        invoice["id"],
        Decimal("1000.00"),
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Payment amount exceeds the outstanding balance"
    )


def test_payment_for_nonexistent_invoice():
    fake_invoice_id = str(uuid4())

    response = create_payment(
        fake_invoice_id,
        Decimal("100.00"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"


def test_payment_rejects_invalid_status():
    invoice = create_test_invoice()

    payment_response = create_payment(
        invoice["id"],
        Decimal("100.00"),
    )

    assert payment_response.status_code == 201

    payment_id = payment_response.json()["id"]

    response = update_payment(
        payment_id,
        "pending",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid payment status transition"
    )

    # The payment must remain pending.
    payment_response = client.get(
        f"/payments/{payment_id}"
    )

    assert payment_response.status_code == 200
    assert payment_response.json()["status"] == "pending"


def test_payment_rejects_invalid_status():
    invoice = create_test_invoice()

    payment_response = create_payment(
        invoice["id"],
        Decimal("100.00"),
    )

    assert payment_response.status_code == 201

    payment_id = payment_response.json()["id"]

    response = update_payment(
        payment_id,
        "pending",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid payment status transition"
    )

    # Verify that the invoice remains unchanged.
    invoice_response = client.get(
        f"/invoices/{invoice['id']}"
    )

    assert invoice_response.status_code == 200

    updated_invoice = invoice_response.json()

    assert Decimal(updated_invoice["amount_paid"]) == Decimal("0.00")
    assert updated_invoice["status"] == "unpaid"

    # Verify that no payment ledger event was created.
    ledger_response = client.get(
        f"/ledger/invoice/{invoice['id']}"
    )

    assert ledger_response.status_code == 200

    ledger_entries = ledger_response.json()

    assert len(ledger_entries) == 1
    assert ledger_entries[0]["entry_type"] == "invoice_created"


def test_payment_cannot_exceed_remaining_balance():
    invoice = create_test_invoice()

    # First payment: ₹700
    first_payment_response = create_payment(
        invoice["id"],
        Decimal("700.00"),
    )

    assert first_payment_response.status_code == 201

    first_payment_id = first_payment_response.json()["id"]

    # Process the first payment successfully.
    first_update_response = update_payment(
        first_payment_id,
        "succeeded",
        provider_reference=f"PAY-FIRST-{uuid4().hex}",
    )

    assert first_update_response.status_code == 200

    # Remaining balance is ₹299.
    # Attempt to create a payment for ₹300.
    second_payment_response = create_payment(
        invoice["id"],
        Decimal("300.00"),
    )

    assert second_payment_response.status_code == 400

    assert second_payment_response.json()["detail"] == (
        "Payment amount exceeds the outstanding balance"
    )

    # Verify that the invoice remains partially paid.
    invoice_response = client.get(
        f"/invoices/{invoice['id']}"
    )

    assert invoice_response.status_code == 200

    updated_invoice = invoice_response.json()

    assert Decimal(updated_invoice["amount_paid"]) == Decimal("700.00")
    assert updated_invoice["status"] == "partially_paid"


def test_successful_payment_rolls_back_when_ledger_creation_fails(
    monkeypatch,
):
    invoice = create_test_invoice()
    payment = create_payment(
        invoice["id"],
        amount="999.00",
    )

    def fail_ledger_creation(*args, **kwargs):
        raise RuntimeError("Simulated ledger failure")

    monkeypatch.setattr(
        "app.services.payment_service.ledger_service.create_ledger_entry",
        fail_ledger_creation,
    )

    # The API request should raise because the test client
    # propagates unhandled server exceptions.
    with pytest.raises(RuntimeError, match="Simulated ledger failure"):
        update_payment(
            payment["id"],
            status="succeeded",
        )

    # The invoice should remain unchanged after rollback.
    updated_invoice = client.get(
        f"/invoices/{invoice['id']}"
    )
    assert updated_invoice.status_code == 200

    invoice_data = updated_invoice.json()
    assert invoice_data["amount_paid"] == "0.00"
    assert invoice_data["status"] == "unpaid"

    # The failed transaction should not add a payment_success
    # ledger entry.
    ledger_response = client.get(
        f"/ledger/invoices/{invoice['id']}"
    )
    assert ledger_response.status_code == 200

    ledger_entries = ledger_response.json()
    assert len(ledger_entries) == 1
    assert ledger_entries[0]["entry_type"] == "invoice_created"



def test_successful_payment_rolls_back_when_ledger_creation_fails(
    monkeypatch,
):
    invoice = create_test_invoice()

    payment_response = create_payment(
        invoice["id"],
        amount="999.00",
    )

    assert payment_response.status_code == 201
    payment = payment_response.json()

    def fail_ledger_creation(*args, **kwargs):
        raise RuntimeError("Simulated ledger failure")

    monkeypatch.setattr(
        "app.services.payment_service.ledger_service.create_ledger_entry",
        fail_ledger_creation,
    )

    # The test client propagates unhandled server exceptions.
    with pytest.raises(RuntimeError, match="Simulated ledger failure"):
        update_payment(
            payment["id"],
            status="succeeded",
        )

    # Verify that the invoice balance and status were rolled back.
    updated_invoice = client.get(
        f"/invoices/{invoice['id']}"
    )
    assert updated_invoice.status_code == 200

    invoice_data = updated_invoice.json()
    assert invoice_data["amount_paid"] == "0.00"
    assert invoice_data["status"] == "unpaid"

    # Only the invoice-created ledger entry should remain.
    ledger_response = client.get(
        f"/ledger/invoice/{invoice['id']}"
    )
    assert ledger_response.status_code == 200

    ledger_entries = ledger_response.json()
    assert len(ledger_entries) == 1
    assert ledger_entries[0]["entry_type"] == "invoice_created"
