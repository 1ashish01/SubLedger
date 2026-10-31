
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
from app.services import customer_service


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    return customer_service.create_customer(
        db,
        customer_data,
    )


@router.get(
    "/",
    response_model=list[CustomerResponse],
)
def get_all_customers(
    db: Session = Depends(get_db),
):
    return customer_service.get_all_customers(db)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    return customer_service.get_customer(
        db,
        customer_id,
    )


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    return customer_service.update_customer(
        db,
        customer_id,
        customer_data,
    )


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    customer_service.delete_customer(
        db,
        customer_id,
    )
