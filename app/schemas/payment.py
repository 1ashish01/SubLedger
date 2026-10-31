
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentAttemptCreate(BaseModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class PaymentAttemptUpdate(BaseModel):
    status: str = Field(pattern="^(pending|succeeded|failed)$")
    provider_reference: str | None = Field(default=None, max_length=100)
    failure_reason: str | None = None


class PaymentAttemptResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    amount: Decimal
    currency: str
    status: str
    provider_reference: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
