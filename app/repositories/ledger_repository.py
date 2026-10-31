
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ledger_entry import LedgerEntry


def create_ledger_entry(
    db: Session,
    entry: LedgerEntry,
) -> LedgerEntry:
    db.add(entry)

    # The service that creates the entry controls the transaction.
    return entry


def get_ledger_entry_by_id(
    db: Session,
    entry_id: UUID,
) -> LedgerEntry | None:
    return (
        db.query(LedgerEntry)
        .filter(LedgerEntry.id == entry_id)
        .first()
    )


def get_ledger_entries_by_customer(
    db: Session,
    customer_id: UUID,
) -> list[LedgerEntry]:
    return (
        db.query(LedgerEntry)
        .filter(LedgerEntry.customer_id == customer_id)
        .order_by(LedgerEntry.created_at.desc())
        .all()
    )


def get_ledger_entries_by_invoice(
    db: Session,
    invoice_id: UUID,
) -> list[LedgerEntry]:
    return (
        db.query(LedgerEntry)
        .filter(LedgerEntry.invoice_id == invoice_id)
        .order_by(LedgerEntry.created_at.desc())
        .all()
    )
