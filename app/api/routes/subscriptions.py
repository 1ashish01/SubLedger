
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
)
from app.services import subscription_service


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.post(
    "/",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subscription(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
):
    return subscription_service.create_subscription(
        db,
        subscription_data,
    )


@router.get(
    "/",
    response_model=list[SubscriptionResponse],
)
def get_all_subscriptions(
    db: Session = Depends(get_db),
):
    return subscription_service.get_all_subscriptions(db)


@router.get(
    "/customer/{customer_id}",
    response_model=list[SubscriptionResponse],
)
def get_subscriptions_by_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    return subscription_service.get_subscriptions_by_customer(
        db,
        customer_id,
    )


@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse,
)
def get_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db),
):
    return subscription_service.get_subscription(
        db,
        subscription_id,
    )


@router.patch(
    "/{subscription_id}",
    response_model=SubscriptionResponse,
)
def update_subscription(
    subscription_id: UUID,
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
):
    return subscription_service.update_subscription(
        db,
        subscription_id,
        subscription_data,
    )
