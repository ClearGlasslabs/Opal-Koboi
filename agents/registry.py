"""Tenant-isolated, fail-closed agent registry."""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class AgentStatus(StrEnum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    QUARANTINED = "quarantined"
    RETIRED = "retired"


class HealthState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"


class AgentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    agent_id: str = Field(pattern=r"^agt_[a-z0-9_-]{3,64}$")
    tenant_id: str = Field(min_length=3)
    codename: str = Field(min_length=2, max_length=64)
    role: str = Field(min_length=2)
    permissions: frozenset[str] = Field(default_factory=frozenset)
    mission_scope: frozenset[str] = Field(min_length=1)
    memory_partition: str = Field(pattern=r"^mem://[a-zA-Z0-9/_-]+$")
    status: AgentStatus = AgentStatus.PROVISIONING
    health: HealthState = HealthState.HEALTHY
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revision: int = Field(default=1, ge=1)

    @field_validator("last_heartbeat")
    @classmethod
    def heartbeat_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("last_heartbeat must be timezone-aware")
        return value


class AgentRegistry:
    """Reference registry; production adapters persist encrypted records in Foundry."""

    def __init__(self, signing_key: SecretStr, heartbeat_ttl: timedelta = timedelta(seconds=90)) -> None:
        if len(signing_key.get_secret_value()) < 32:
            raise ValueError("registry signing key must contain at least 32 characters")
        self._key = signing_key.get_secret_value().encode()
        self._ttl = heartbeat_ttl
        self._records: dict[tuple[str, str], AgentRecord] = {}

    def register(self, record: AgentRecord) -> str:
        key = (record.tenant_id, record.agent_id)
        if key in self._records:
            raise ValueError("agent already registered in tenant")
        self._records[key] = record
        return self.attestation(record)

    def resolve(self, tenant_id: str, agent_id: str) -> AgentRecord:
        try:
            record = self._records[(tenant_id, agent_id)]
        except KeyError as exc:
            raise PermissionError("agent is not registered for tenant") from exc
        now = datetime.now(timezone.utc)
        if record.status != AgentStatus.ACTIVE or now - record.last_heartbeat > self._ttl:
            raise PermissionError("agent is inactive or heartbeat is stale")
        return record

    def heartbeat(self, tenant_id: str, agent_id: str, attestation: str) -> AgentRecord:
        record = self._records.get((tenant_id, agent_id))
        if record is None or not hmac.compare_digest(attestation, self.attestation(record)):
            raise PermissionError("invalid agent attestation")
        updated = record.model_copy(update={"last_heartbeat": datetime.now(timezone.utc), "revision": record.revision + 1})
        self._records[(tenant_id, agent_id)] = updated
        return updated

    def attestation(self, record: AgentRecord) -> str:
        payload = json.dumps(record.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hmac.new(self._key, payload.encode(), hashlib.sha256).hexdigest()
