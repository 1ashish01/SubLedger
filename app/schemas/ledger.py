
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LedgerEntryResponse(BaseModel):
    id: UUID
    customer_id: UUID
    invoice_id: UUID | None
    entry_type: str
    amount: Decimal
    currency: str
    reference_id: UUID
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
