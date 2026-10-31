from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


def create_customer(db: Session, customer: Customer) -> Customer:
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer_by_id(
    db: Session,
    customer_id,
) -> Customer | None:
    statement = select(Customer).where(Customer.id == customer_id)
    return db.scalar(statement)


def get_customer_by_email(
    db: Session,
    email: str,
) -> Customer | None:
    statement = select(Customer).where(Customer.email == email)
    return db.scalar(statement)


def get_all_customers(db: Session) -> list[Customer]:
    statement = select(Customer).order_by(Customer.created_at.desc())
    return list(db.scalars(statement).all())


def update_customer(db: Session, customer: Customer) -> Customer:
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: Customer) -> None:
    db.delete(customer)
    db.commit()