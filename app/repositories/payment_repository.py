from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_attempt import PaymentAttempt


def create_payment_attempt(
    db: Session,
    payment: PaymentAttempt,
) -> PaymentAttempt:
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment



def get_payment_attempt_by_id(
    db: Session,
    payment_id,
    for_update: bool = False,
) -> PaymentAttempt | None:
    statement = select(PaymentAttempt).where(
        PaymentAttempt.id == payment_id
    )

    if for_update:
        statement = statement.with_for_update()

    return db.scalar(statement)


def get_payments_by_invoice(
    db: Session,
    invoice_id,
) -> list[PaymentAttempt]:
    statement = (
        select(PaymentAttempt)
        .where(PaymentAttempt.invoice_id == invoice_id)
        .order_by(PaymentAttempt.created_at.desc())
    )
    return list(db.scalars(statement).all())



def update_payment_attempt(
    db: Session,
    payment: PaymentAttempt,
) -> PaymentAttempt:
    db.add(payment)
    return payment

    