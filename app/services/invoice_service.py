
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.repositories import (
    invoice_repository,
    subscription_repository,
)
from app.schemas.invoice import InvoiceCreate
from app.services import ledger_service


def create_invoice(
    db: Session,
    invoice_data: InvoiceCreate,
) -> Invoice:
    try:
        # Verify that the subscription exists.
        subscription = subscription_repository.get_subscription_by_id(
            db,
            invoice_data.subscription_id,
        )

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found",
            )

        # Only active subscriptions can generate invoices.
        if subscription.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create invoice for an inactive subscription",
            )

        # Retrieve the plan associated with the subscription.
        plan = subscription.plan

        # Generate a unique invoice number.
        invoice_number = f"INV-{uuid4().hex[:12].upper()}"

        # Snapshot the current plan price in the invoice.
        invoice = Invoice(
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            invoice_number=invoice_number,
            total_amount=plan.price,
            amount_paid=0,
            currency=plan.currency,
            status="unpaid",
            due_date=invoice_data.due_date,
        )

        # Add the invoice to the current transaction.
        invoice_repository.create_invoice(
            db,
            invoice,
        )

        # Flush so the invoice is persisted within the transaction
        # and its ID is available for the ledger entry.
        db.flush()

        # Record the invoice creation event.
        ledger_service.create_ledger_entry(
            db=db,
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            reference_id=invoice.id,
            amount=invoice.total_amount,
            currency=invoice.currency,
            entry_type="invoice_created",
            description=(
                f"Invoice {invoice.invoice_number} created"
            ),
        )

        # Commit the invoice and ledger event together.
        db.commit()
        db.refresh(invoice)

        return invoice

    except Exception:
        # Roll back both invoice and ledger changes on failure.
        db.rollback()
        raise


def get_invoice(
    db: Session,
    invoice_id,
) -> Invoice:
    invoice = invoice_repository.get_invoice_by_id(
        db,
        invoice_id,
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return invoice


def get_invoices_by_customer(
    db: Session,
    customer_id,
) -> list[Invoice]:
    return invoice_repository.get_invoices_by_customer(
        db,
        customer_id,
    )


def get_invoices_by_subscription(
    db: Session,
    subscription_id,
) -> list[Invoice]:
    return invoice_repository.get_invoices_by_subscription(
        db,
        subscription_id,
    )
