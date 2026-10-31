from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invoice import Invoice


def create_invoice(db: Session, invoice: Invoice) -> Invoice:
    db.add(invoice)
    return invoice



def get_invoice_by_id(
    db: Session,
    invoice_id,
    for_update: bool = False,
) -> Invoice | None:
    statement = select(Invoice).where(
        Invoice.id == invoice_id
    )

    if for_update:
        statement = statement.with_for_update()

    return db.scalar(statement)


def get_invoice_by_number(
    db: Session,
    invoice_number: str,
) -> Invoice | None:
    statement = select(Invoice).where(
        Invoice.invoice_number == invoice_number
    )
    return db.scalar(statement)


def get_invoices_by_customer(
    db: Session,
    customer_id,
) -> list[Invoice]:
    statement = (
        select(Invoice)
        .where(Invoice.customer_id == customer_id)
        .order_by(Invoice.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_invoices_by_subscription(
    db: Session,
    subscription_id,
) -> list[Invoice]:
    statement = (
        select(Invoice)
        .where(Invoice.subscription_id == subscription_id)
        .order_by(Invoice.created_at.desc())
    )
    return list(db.scalars(statement).all())



def update_invoice(
    db: Session,
    invoice: Invoice,
) -> Invoice:
    db.add(invoice)
    return invoice
