"""Deterministic task, action, escalation, and output policy."""
from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class PolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str
    actor_id: str
    roles: frozenset[str]
    permissions: frozenset[str]
    mission_id: str
    action: str
    risk_score: int = Field(ge=0, le=100)
    sensitive: bool = False
    output: str | None = None


class PolicyResult(BaseModel):
    decision: Decision
    reasons: tuple[str, ...]
    sanitized_output: str | None = None
    obligations: tuple[str, ...] = ("append_audit_event", "propagate_trace")


class PolicyEngine:
    """Fails closed: explicit permission plus escalation policy is mandatory."""

    _SECRET = re.compile(r"(?i)(api[_-]?key|token|password)\s*[:=]\s*[^\s,;]+")

    def evaluate(self, request: PolicyRequest) -> PolicyResult:
        reasons: list[str] = []
        if f"action:{request.action}" not in request.permissions:
            reasons.append("missing explicit action permission")
        if request.sensitive and "security_steward" not in request.roles:
            reasons.append("sensitive operation requires security steward")
        sanitized = self._SECRET.sub(r"\1=[REDACTED]", request.output) if request.output else None
        if reasons:
            return PolicyResult(decision=Decision.DENY, reasons=tuple(reasons), sanitized_output=sanitized)
        if request.risk_score >= 70:
            return PolicyResult(
                decision=Decision.REQUIRE_APPROVAL,
                reasons=("risk exceeds human approval threshold",),
                sanitized_output=sanitized,
                obligations=("append_audit_event", "propagate_trace", "capture_two_person_approval"),
            )
        return PolicyResult(decision=Decision.ALLOW, reasons=("policy checks passed",), sanitized_output=sanitized)
