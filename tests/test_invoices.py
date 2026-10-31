
from uuid import uuid4
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_invoice_for_valid_subscription():
    unique_id = uuid4().hex

    # Create a customer
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Invoice Test Customer",
            "email": f"invoice_{unique_id}@example.com",
            "phone": "9876543210",
        },
    )

    assert customer_response.status_code == 201
    customer_id = customer_response.json()["id"]

    # Create an active plan
    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Invoice Plan {unique_id}",
            "description": "Plan for invoice testing",
            "billing_cycle": "monthly",
            "price": "999.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201
    plan_id = plan_response.json()["id"]

    # Create a subscription
    subscription_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert subscription_response.status_code == 201
    subscription_id = subscription_response.json()["id"]

    # Create an invoice for the subscription
    invoice_response = client.post(
        "/invoices/",
        json={
            "subscription_id": subscription_id,
        },
    )

    assert invoice_response.status_code == 201

    invoice = invoice_response.json()

    assert invoice["customer_id"] == customer_id
    assert invoice["subscription_id"] == subscription_id
    assert Decimal(invoice["total_amount"]) == Decimal("999.00")
    assert Decimal(invoice["amount_paid"]) == Decimal("0.00")
    assert invoice["currency"] == "INR"
    assert invoice["status"] == "unpaid"


def test_create_invoice_for_nonexistent_subscription():
    fake_subscription_id = str(uuid4())

    response = client.post(
        "/invoices/",
        json={
            "subscription_id": fake_subscription_id,
        },
    )

    assert response.status_code == 404


def test_invoice_preserves_price_after_plan_price_changes():
    unique_id = uuid4().hex

    # Create customer
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Snapshot Test Customer",
            "email": f"snapshot_{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201
    customer_id = customer_response.json()["id"]

    # Create plan with initial price
    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Snapshot Plan {unique_id}",
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
    invoice_id = invoice_response.json()["id"]

    # Update the plan price
    update_response = client.patch(
        f"/plans/{plan_id}",
        json={
            "price": "1499.00",
        },
    )

    assert update_response.status_code == 200

    # Retrieve the existing invoice
    invoice_response = client.get(
        f"/invoices/{invoice_id}",
    )

    assert invoice_response.status_code == 200

    invoice = invoice_response.json()

    # Existing invoice must retain its original price
    assert Decimal(invoice["total_amount"]) == Decimal("999.00")
    assert invoice["currency"] == "INR"



def test_get_invoice_by_id():
    unique_id = uuid4().hex

    # Create customer
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Get Invoice Customer",
            "email": f"get_invoice_{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201
    customer_id = customer_response.json()["id"]

    # Create plan
    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Get Invoice Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "499.00",
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
    invoice_id = invoice_response.json()["id"]

    # Retrieve invoice by ID
    response = client.get(f"/invoices/{invoice_id}")

    assert response.status_code == 200

    invoice = response.json()

    assert invoice["id"] == invoice_id
    assert invoice["customer_id"] == customer_id
    assert invoice["subscription_id"] == subscription_id
    assert Decimal(invoice["total_amount"]) == Decimal("499.00")


def test_get_invoices_by_customer():
    unique_id = uuid4().hex

    # Create customer
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Customer Invoice List",
            "email": f"customer_invoice_{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201
    customer_id = customer_response.json()["id"]

    # Create plan
    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Customer Invoice Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "799.00",
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
    invoice_id = invoice_response.json()["id"]

    # Retrieve invoices by customer
    response = client.get(
        f"/invoices/customer/{customer_id}",
    )

    assert response.status_code == 200

    invoices = response.json()

    assert isinstance(invoices, list)
    assert any(invoice["id"] == invoice_id for invoice in invoices)

    # Every returned invoice should belong to this customer
    assert all(
        invoice["customer_id"] == customer_id
        for invoice in invoices
    )



def test_get_invoices_by_subscription():
    unique_id = uuid4().hex

    # Create customer
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Subscription Invoice Customer",
            "email": f"subscription_invoice_{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201
    customer_id = customer_response.json()["id"]

    # Create plan
    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Subscription Invoice Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "599.00",
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
    invoice_id = invoice_response.json()["id"]

    # Retrieve invoices by subscription
    response = client.get(
        f"/invoices/subscription/{subscription_id}",
    )

    assert response.status_code == 200

    invoices = response.json()

    assert isinstance(invoices, list)
    assert any(invoice["id"] == invoice_id for invoice in invoices)

    # Every returned invoice should belong to this subscription
    assert all(
        invoice["subscription_id"] == subscription_id
        for invoice in invoices
    )


def test_get_nonexistent_invoice():
    fake_invoice_id = str(uuid4())

    response = client.get(
        f"/invoices/{fake_invoice_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"


def test_invoice_filter_routes_are_not_matched_as_invoice_id():
    fake_customer_id = str(uuid4())
    fake_subscription_id = str(uuid4())

    customer_response = client.get(
        f"/invoices/customer/{fake_customer_id}",
    )

    subscription_response = client.get(
        f"/invoices/subscription/{fake_subscription_id}",
    )

    assert customer_response.status_code == 200
    assert subscription_response.status_code == 200
