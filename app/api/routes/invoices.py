
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.services import invoice_service


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


@router.post(
    "/",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
):
    return invoice_service.create_invoice(
        db,
        invoice_data,
    )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
):
    return invoice_service.get_invoice(
        db,
        invoice_id,
    )


@router.get(
    "/customer/{customer_id}",
    response_model=list[InvoiceResponse],
)
def get_invoices_by_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    return invoice_service.get_invoices_by_customer(
        db,
        customer_id,
    )


@router.get(
    "/subscription/{subscription_id}",
    response_model=list[InvoiceResponse],
)
def get_invoices_by_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db),
):
    return invoice_service.get_invoices_by_subscription(
        db,
        subscription_id,
    )
