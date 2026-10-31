
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories import customer_repository
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(
    db: Session,
    customer_data: CustomerCreate,
) -> Customer:
    existing_customer = customer_repository.get_customer_by_email(
        db,
        str(customer_data.email),
    )

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists",
        )

    customer = Customer(**customer_data.model_dump())

    return customer_repository.create_customer(db, customer)


def get_customer(db: Session, customer_id) -> Customer:
    customer = customer_repository.get_customer_by_id(
        db,
        customer_id,
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


def get_all_customers(db: Session) -> list[Customer]:
    return customer_repository.get_all_customers(db)


def update_customer(
    db: Session,
    customer_id,
    customer_data: CustomerUpdate,
) -> Customer:
    customer = get_customer(db, customer_id)

    update_data = customer_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        update_data["email"] = str(update_data["email"])

        existing_customer = customer_repository.get_customer_by_email(
            db,
            update_data["email"],
        )

        if (
            existing_customer
            and existing_customer.id != customer.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this email already exists",
            )

    for field, value in update_data.items():
        setattr(customer, field, value)

    return customer_repository.update_customer(db, customer)


def delete_customer(db: Session, customer_id) -> None:
    customer = get_customer(db, customer_id)

    customer_repository.delete_customer(db, customer)

