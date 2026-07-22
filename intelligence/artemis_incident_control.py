"""Deterministic incident lifecycle controls for ClearGlassInc Artemis.

The module models the autonomous-systems safety envelope around the required
DETECT → VALIDATE → CORRELATE → CLASSIFY → CONTAIN → PLAN → AUTHORIZE → EXECUTE →
VERIFY → MONITOR → CLOSE/ROLLBACK/ESCALATE lifecycle. It is deliberately pure
Python: callers can persist the returned receipts in any append-only store and can
run the same checks in API handlers, workers, replay jobs, and deployment gates.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LifecycleStage(StrEnum):
    DETECT = "detect"
    VALIDATE = "validate"
    CORRELATE = "correlate"
    CLASSIFY = "classify"
    CONTAIN = "contain"
    PLAN = "plan"
    AUTHORIZE = "authorize"
    EXECUTE = "execute"
    VERIFY = "verify"
    MONITOR = "monitor"
    CLOSE = "close"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"


class IncidentSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentEvidence(StrictModel):
    evidence_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signal_type: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    content_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    provenance: dict[str, Any] = Field(default_factory=dict)


class IncidentContext(StrictModel):
    incident_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    current_stage: LifecycleStage
    severity: IncidentSeverity
    evidence: list[IncidentEvidence] = Field(min_length=1)
    affected_assets: set[str] = Field(default_factory=set)
    correlated_event_ids: set[str] = Field(default_factory=set)

    @property
    def minimum_confidence(self) -> float:
        return min(item.confidence for item in self.evidence)


class RecoveryAction(StrictModel):
    action_id: str = Field(min_length=1)
    action_type: Literal["containment", "remediation", "verification", "rollback", "escalation"]
    stage: LifecycleStage
    scope: set[str] = Field(min_length=1)
    idempotency_key: str = Field(min_length=16)
    timeout_seconds: int = Field(gt=0, le=3600)
    max_attempts: int = Field(ge=1, le=5)
    blast_radius_ceiling: int = Field(ge=1)
    rollback_strategy: str = Field(min_length=12)
    requires_human_approval: bool = False
    approved_by: str | None = None
    approval_ticket: str | None = None
    kill_switch_engaged: bool = False

    @model_validator(mode="after")
    def enforce_approval_fields(self) -> "RecoveryAction":
        if self.requires_human_approval and (not self.approved_by or not self.approval_ticket):
            raise ValueError("high-impact actions require approved_by and approval_ticket")
        return self


class ActionDecision(StrictModel):
    decision: Literal["allow", "deny"]
    reasons: list[str]
    obligations: list[str]
    receipt_hash: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=sorted)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def classify_incident(evidence: list[IncidentEvidence], *, affected_asset_count: int) -> IncidentSeverity:
    """Classify incidents deterministically from validated evidence only."""

    if not evidence:
        raise ValueError("classification requires validated evidence")
    max_confidence = max(item.confidence for item in evidence)
    signal_types = {item.signal_type.lower() for item in evidence}
    if max_confidence >= 0.9 and affected_asset_count >= 25:
        return IncidentSeverity.CRITICAL
    if {"policy_denial_spike", "service_unavailable", "data_integrity"}.intersection(signal_types):
        return IncidentSeverity.HIGH if max_confidence >= 0.75 else IncidentSeverity.MEDIUM
    if max_confidence >= 0.7 or affected_asset_count >= 5:
        return IncidentSeverity.MEDIUM
    return IncidentSeverity.LOW


def evaluate_recovery_action(context: IncidentContext, action: RecoveryAction) -> ActionDecision:
    """Fail closed before any autonomous recovery action is dispatched."""

    reasons: list[str] = []
    obligations = [
        "append tamper-evident audit receipt",
        "propagate tenant_id mission_id incident_id idempotency_key trace_id",
        "run independent verification before close",
    ]

    if action.kill_switch_engaged:
        reasons.append("automation kill switch is engaged")
    if context.minimum_confidence < 0.6 and action.action_type != "escalation":
        reasons.append("validated evidence confidence is below autonomous threshold")
    if action.stage.value not in {stage.value for stage in LifecycleStage}:
        reasons.append("action stage is not in lifecycle")
    if action.action_type == "remediation" and context.current_stage.value not in {LifecycleStage.CONTAIN.value, LifecycleStage.PLAN.value, LifecycleStage.AUTHORIZE.value, LifecycleStage.EXECUTE.value}:
        reasons.append("remediation cannot run before containment planning")
    if action.action_type == "remediation" and LifecycleStage.CONTAIN.value != context.current_stage.value and context.severity in {IncidentSeverity.HIGH, IncidentSeverity.CRITICAL}:
        obligations.append("prove containment was completed before remediation")
    if len(action.scope) > action.blast_radius_ceiling:
        reasons.append("action scope exceeds blast-radius ceiling")
    if context.affected_assets and not action.scope.issubset(context.affected_assets):
        reasons.append("action scope includes assets outside incident blast radius")
    if context.severity in {IncidentSeverity.HIGH, IncidentSeverity.CRITICAL} and not action.requires_human_approval:
        reasons.append("high-impact incident action requires human approval")

    receipt_hash = _stable_hash(
        {
            "incident_id": context.incident_id,
            "tenant_id": context.tenant_id,
            "mission_id": context.mission_id,
            "stage": context.current_stage.value,
            "severity": context.severity.value,
            "action_id": action.action_id,
            "action_type": action.action_type,
            "scope": sorted(action.scope),
            "idempotency_key": action.idempotency_key,
            "reasons": reasons,
            "obligations": obligations,
            "evidence_hashes": [item.content_hash for item in context.evidence],
        }
    )
    return ActionDecision(
        decision="deny" if reasons else "allow",
        reasons=reasons or ["recovery action is bounded, attributable, and ready for dispatch"],
        obligations=obligations,
        receipt_hash=receipt_hash,
    )
