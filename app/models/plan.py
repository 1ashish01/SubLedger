
from decimal import Decimal

from sqlalchemy import CheckConstraint, String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseEntity


class Plan(BaseEntity):
    __tablename__ = "plans"

    __table_args__ = (
        CheckConstraint("price > 0", name="ck_plans_price_positive"),
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    billing_cycle: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )
