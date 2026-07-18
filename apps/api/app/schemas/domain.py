from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.domain import ApprovalStatus


class ActorContext(BaseModel):
    actor: str = Field(min_length=2, max_length=255)
    request_id: str = Field(min_length=8, max_length=128)


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


class ApprovalDecision(BaseModel):
    actor: str = Field(min_length=2, max_length=255)
    reason: str = Field(min_length=3, max_length=2000)


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    request_id: str
    actor: str
    action: str
    target_type: str
    target_id: str
    payload: dict[str, Any]
    risk_score: int
    status: ApprovalStatus
    decided_by: str | None
    decision_reason: str | None
    created_at: datetime
    decided_at: datetime | None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    request_id: str
    actor: str
    action: str
    target: str
    payload: dict[str, Any] | None
    result: str
    risk_score: int
    previous_hash: str
    event_hash: str
    created_at: datetime
