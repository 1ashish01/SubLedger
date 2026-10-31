
from decimal import Decimal
from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlanCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    billing_cycle: Literal["monthly", "yearly"]
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    status: Literal["active", "inactive"] = "active"


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    billing_cycle: Literal["monthly", "yearly"] | None = None
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    status: Literal["active", "inactive"] | None = None


class PlanResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    billing_cycle: str
    price: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
