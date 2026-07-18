from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.approval import ApprovalStatus


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
