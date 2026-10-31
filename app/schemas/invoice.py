
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InvoiceCreate(BaseModel):
    subscription_id: UUID
    due_date: datetime | None = None


class InvoiceResponse(BaseModel):
    id: UUID
    customer_id: UUID
    subscription_id: UUID
    invoice_number: str
    total_amount: Decimal
    amount_paid: Decimal
    currency: str
    status: str
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoicePaymentSummary(BaseModel):
    invoice_id: UUID
    total_amount: Decimal
    amount_paid: Decimal
    outstanding_balance: Decimal
    status: str
