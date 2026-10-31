
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ledger import LedgerEntryResponse
from app.services import ledger_service


router = APIRouter(
    prefix="/ledger",
    tags=["Ledger"],
)


@router.get(
    "/customer/{customer_id}",
    response_model=list[LedgerEntryResponse],
)
def get_ledger_entries_by_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    return ledger_service.get_ledger_entries_by_customer(
        db,
        customer_id,
    )


@router.get(
    "/invoice/{invoice_id}",
    response_model=list[LedgerEntryResponse],
)
def get_ledger_entries_by_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
):
    return ledger_service.get_ledger_entries_by_invoice(
        db,
        invoice_id,
    )


@router.get(
    "/{entry_id}",
    response_model=LedgerEntryResponse,
)
def get_ledger_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
):
    return ledger_service.get_ledger_entry(
        db,
        entry_id,
    )
