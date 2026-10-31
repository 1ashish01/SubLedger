
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionCreate(BaseModel):
    customer_id: UUID
    plan_id: UUID


class SubscriptionUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=20)
    end_date: datetime | None = None


class SubscriptionResponse(BaseModel):
    id: UUID
    customer_id: UUID
    plan_id: UUID
    start_date: datetime
    end_date: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
