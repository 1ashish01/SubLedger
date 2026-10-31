
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import (
    PaymentAttemptCreate,
    PaymentAttemptResponse,
    PaymentAttemptUpdate,
)
from app.services import payment_service


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "/",
    response_model=PaymentAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_attempt(
    payment_data: PaymentAttemptCreate,
    db: Session = Depends(get_db),
):
    return payment_service.create_payment_attempt(
        db,
        payment_data,
    )


@router.patch(
    "/{payment_id}",
    response_model=PaymentAttemptResponse,
)
def update_payment_attempt_status(
    payment_id: UUID,
    payment_data: PaymentAttemptUpdate,
    db: Session = Depends(get_db),
):
    return payment_service.update_payment_attempt_status(
        db,
        payment_id,
        payment_data,
    )
