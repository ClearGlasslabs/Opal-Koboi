"""Plugin contract for read-only intelligence connectors."""
from __future__ import annotations

from typing import Protocol

from executive.event_bus import EventEnvelope


class IntelligenceConnector(Protocol):
    name: str

    async def healthcheck(self) -> bool: ...

    async def collect(self, *, tenant_id: str, mission_id: str, cursor: str | None) -> tuple[list[EventEnvelope], str]: ...
