from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus
from app.schemas.common import ActorContext


class OrderCreate(ActorContext):
    external_reference: str | None = Field(default=None, max_length=128)
    currency: str = Field(default="CAD", min_length=3, max_length=3)
    total_amount: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    external_reference: str | None
    status: OrderStatus
    currency: str
    total_amount: Decimal
    version: int
    created_at: datetime
    updated_at: datetime
