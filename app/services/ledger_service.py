from decimal import Decimal
from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ledger_entry import LedgerEntry
from app.repositories import ledger_repository


LedgerEventType = Literal[
    "invoice_created",
    "payment_success",
    "payment_failure",
]


def create_ledger_entry(
    db: Session,
    customer_id: UUID,
    invoice_id: UUID,
    reference_id: UUID,
    amount: Decimal,
    currency: str,
    entry_type: LedgerEventType,
    description: str,
) -> LedgerEntry:
    entry = LedgerEntry(
        customer_id=customer_id,
        invoice_id=invoice_id,
        entry_type=entry_type,
        amount=amount,
        currency=currency,
        reference_id=reference_id,
        description=description,
    )

    # Add the entry to the current transaction.
    # The calling service is responsible for committing.
    return ledger_repository.create_ledger_entry(
        db,
        entry,
    )


def get_ledger_entry(
    db: Session,
    entry_id: UUID,
) -> LedgerEntry | None:
    return ledger_repository.get_ledger_entry_by_id(
        db,
        entry_id,
    )


def get_ledger_entries_by_customer(
    db: Session,
    customer_id: UUID,
) -> list[LedgerEntry]:
    return ledger_repository.get_ledger_entries_by_customer(
        db,
        customer_id,
    )


def get_ledger_entries_by_invoice(
    db: Session,
    invoice_id: UUID,
) -> list[LedgerEntry]:
    return ledger_repository.get_ledger_entries_by_invoice(
        db,
        invoice_id,
    )