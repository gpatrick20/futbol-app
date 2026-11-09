from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    user_id: UUID
    amount: Decimal = Field(gt=0)
    method: str | None = Field(default=None, pattern="^(cash|transfer|online)$")


class PaymentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|paid|rejected)$")


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    match_id: UUID
    user_id: UUID
    amount: Decimal
    status: str
    method: str | None
    paid_at: datetime | None
