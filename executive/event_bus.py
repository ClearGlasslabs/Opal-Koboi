"""Typed at-least-once event bus with replay and tenant controls."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventType(StrEnum):
    INTEL_OBSERVED = "intelligence.observed.v1"
    THREAT_CORRELATED = "threat.correlated.v1"
    TASK_PROPOSED = "agent.task.proposed.v1"
    POLICY_DECIDED = "policy.decided.v1"
    APPROVAL_RECORDED = "approval.recorded.v1"


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex}")
    event_type: EventType
    tenant_id: str = Field(min_length=3)
    mission_id: str = Field(min_length=3)
    producer: str = Field(min_length=3)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str = Field(min_length=8)
    schema_version: int = 1
    payload: dict[str, Any]
    idempotency_key: str = Field(min_length=8)


Handler = Callable[[EventEnvelope], Awaitable[None]]


class EventBus:
    """In-process contract adapter mirroring Kafka/NATS production semantics."""

    def __init__(self, replay_window: timedelta = timedelta(minutes=10)) -> None:
        self._handlers: dict[EventType, list[Handler]] = defaultdict(list)
        self._seen: dict[str, datetime] = {}
        self._replay_window = replay_window

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: EventEnvelope) -> int:
        now = datetime.now(timezone.utc)
        self._seen = {key: seen for key, seen in self._seen.items() if now - seen < self._replay_window}
        replay_key = hashlib.sha256(f"{event.tenant_id}:{event.idempotency_key}".encode()).hexdigest()
        if replay_key in self._seen:
            raise ValueError("replayed event rejected")
        if event.occurred_at > now + timedelta(seconds=30) or now - event.occurred_at > self._replay_window:
            raise ValueError("event timestamp outside replay window")
        self._seen[replay_key] = now
        handlers = self._handlers[event.event_type]
        for handler in handlers:
            await handler(event)
        return len(handlers)
