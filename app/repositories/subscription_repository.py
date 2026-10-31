from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription import Subscription


def create_subscription(
    db: Session,
    subscription: Subscription,
) -> Subscription:
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def get_subscription_by_id(
    db: Session,
    subscription_id,
) -> Subscription | None:
    statement = select(Subscription).where(
        Subscription.id == subscription_id
    )
    return db.scalar(statement)


def get_active_subscription(
    db: Session,
    customer_id,
    plan_id,
) -> Subscription | None:
    statement = select(Subscription).where(
        Subscription.customer_id == customer_id,
        Subscription.plan_id == plan_id,
        Subscription.status == "active",
    )
    return db.scalar(statement)


def get_subscriptions_by_customer(
    db: Session,
    customer_id,
) -> list[Subscription]:
    statement = (
        select(Subscription)
        .where(Subscription.customer_id == customer_id)
        .order_by(Subscription.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_all_subscriptions(db: Session) -> list[Subscription]:
    statement = select(Subscription).order_by(
        Subscription.created_at.desc()
    )
    return list(db.scalars(statement).all())


def update_subscription(
    db: Session,
    subscription: Subscription,
) -> Subscription:
    db.commit()
    db.refresh(subscription)
    return subscription