from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.payment_attempt import PaymentAttempt
from app.repositories import (
    invoice_repository,
    payment_repository,
)
from app.schemas.payment import (
    PaymentAttemptCreate,
    PaymentAttemptUpdate,
)
from app.services import ledger_service

def create_payment_attempt(
    db: Session,
    payment_data: PaymentAttemptCreate,
) -> PaymentAttempt:
    # Verify that the invoice exists.
    invoice = invoice_repository.get_invoice_by_id(
        db,
        payment_data.invoice_id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    # Calculate the outstanding balance.
    outstanding_balance = invoice.total_amount - invoice.amount_paid
    # A payment cannot exceed the outstanding balance.
    if payment_data.amount > outstanding_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount exceeds the outstanding balance",
        )
    payment = PaymentAttempt(
        invoice_id=invoice.id,
        amount=payment_data.amount,
        currency=invoice.currency,
        status="pending",
    )
    return payment_repository.create_payment_attempt(
        db,
        payment,
    )
def update_payment_attempt_status(
    db: Session,
    payment_id: UUID,
    payment_data: PaymentAttemptUpdate,) -> PaymentAttempt:
    
    try:
        # Lock the payment row to prevent concurrent processing.
        payment = payment_repository.get_payment_attempt_by_id(
            db,
            payment_id,
            for_update=True,
        )
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment attempt not found",
            )
        # A processed payment cannot be processed again.
        if payment.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment attempt has already been processed",
            )
        # Only succeeded or failed statuses are allowed.
        if payment_data.status not in ("succeeded", "failed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment status transition",
            )
        # Retrieve the invoice associated with this payment.
        invoice = invoice_repository.get_invoice_by_id(
            db,
            payment.invoice_id,
        )
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )
        # Handle failed payments.
        if payment_data.status == "failed":
            payment.status = "failed"
            payment.provider_reference = payment_data.provider_reference
            payment.failure_reason = payment_data.failure_reason
            payment_repository.update_payment_attempt(
                db,
                payment,
            )
            # Record the failed payment without changing the invoice.
            ledger_service.create_ledger_entry(
                db=db,
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                reference_id=payment.id,
                amount=payment.amount,
                currency=payment.currency,
                entry_type="payment_failure",
                description=(
                    f"Payment failed for invoice "
                    f"{invoice.invoice_number}"
                ),
            )
            # Commit the payment and ledger event together.
            db.commit()
            db.refresh(payment)
            return payment
        # Lock the invoice before updating its balance.
        invoice = invoice_repository.get_invoice_by_id(
            db,
            payment.invoice_id,
            for_update=True,
        )
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )
        # Recheck the outstanding balance inside the transaction.
        outstanding_balance = invoice.total_amount - invoice.amount_paid
        if payment.amount > outstanding_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount exceeds the outstanding balance",
            )
        # Mark the payment as successful.
        payment.status = "succeeded"
        payment.provider_reference = payment_data.provider_reference
        payment.failure_reason = None
        payment_repository.update_payment_attempt(
            db,
            payment,
        )
        # Update the invoice balance.
        invoice.amount_paid += payment.amount
        if invoice.amount_paid == invoice.total_amount:
            invoice.status = "paid"
        else:
            invoice.status = "partially_paid"
        invoice_repository.update_invoice(
            db,
            invoice,
        )
        # Record the successful payment.
        ledger_service.create_ledger_entry(
            db=db,
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            reference_id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            entry_type="payment_success",
            description=(
                f"Payment received for invoice "
                f"{invoice.invoice_number}"
            ),
        )
        # Commit all changes together.
        db.commit()
        db.refresh(payment)
        return payment
    except Exception:
        # Roll back all changes if anything fails.
        db.rollback()
        raise
