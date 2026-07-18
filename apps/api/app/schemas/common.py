from __future__ import annotations

from pydantic import BaseModel, Field


class ActorContext(BaseModel):
    actor: str = Field(min_length=2, max_length=255)
    request_id: str = Field(min_length=8, max_length=128)
