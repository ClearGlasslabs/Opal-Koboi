from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """Internal audit-event command.

    Public routes must not accept this schema directly; events are emitted by
    trusted services after the associated business mutation is validated.
    """

    request_id: str = Field(min_length=8, max_length=128)
    actor: str = Field(min_length=2, max_length=255)
    action: str = Field(min_length=1, max_length=128)
    target: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any] | None = None
    result: str = Field(min_length=1, max_length=64)
    risk_score: int = Field(default=0, ge=0, le=100)


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
