
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.repositories import plan_repository, subscription_repository
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


def create_subscription(
    db: Session,
    subscription_data: SubscriptionCreate,
) -> Subscription:
    # Check whether the customer already has an active
    # subscription for this plan.
    existing_subscription = (
        subscription_repository.get_active_subscription(
            db,
            subscription_data.customer_id,
            subscription_data.plan_id,
        )
    )

    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer already has an active subscription for this plan",
        )

    # Verify that the selected plan exists.
    plan = plan_repository.get_plan_by_id(
        db,
        subscription_data.plan_id,
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )

    # An inactive plan cannot be subscribed to.
    if plan.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot subscribe to an inactive plan",
        )

    subscription = Subscription(
        customer_id=subscription_data.customer_id,
        plan_id=subscription_data.plan_id,
        start_date=datetime.now(timezone.utc),
        status="active",
    )

    return subscription_repository.create_subscription(
        db,
        subscription,
    )


def get_subscription(
    db: Session,
    subscription_id,
) -> Subscription:
    subscription = subscription_repository.get_subscription_by_id(
        db,
        subscription_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    return subscription


def get_subscriptions_by_customer(
    db: Session,
    customer_id,
) -> list[Subscription]:
    return subscription_repository.get_subscriptions_by_customer(
        db,
        customer_id,
    )


def get_all_subscriptions(
    db: Session,
) -> list[Subscription]:
    return subscription_repository.get_all_subscriptions(db)


def update_subscription(
    db: Session,
    subscription_id,
    subscription_data: SubscriptionUpdate,
) -> Subscription:
    subscription = get_subscription(db, subscription_id)

    update_data = subscription_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(subscription, field, value)

    return subscription_repository.update_subscription(
        db,
        subscription,
    )
