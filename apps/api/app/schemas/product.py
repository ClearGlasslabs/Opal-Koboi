from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ActorContext


class ProductCreate(ActorContext):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=10000)
    price: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    inventory_count: int = Field(default=0, ge=0)


class ProductUpdate(ActorContext):
    expected_version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    price: Decimal | None = Field(default=None, ge=0, max_digits=18, decimal_places=2)
    inventory_count: int | None = Field(default=None, ge=0)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    price: Decimal
    inventory_count: int
    version: int
    created_at: datetime
    updated_at: datetime


class MutationResult(BaseModel):
    status: str
    product: ProductRead | None = None
    approval_id: str | None = None
    risk_score: int
