"""Mission-scoped policy engine for ClearGlassInc Artemis.

The policy layer is intentionally deterministic and model-independent. AI agents may
propose actions, but every consequential tool call must pass this gate with an
operator/workload identity, mission context, compartment markings, and an audit hash.
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


class Classification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    REGULATED = "regulated"
    MISSION_CRITICAL = "mission_critical"


CLASSIFICATION_RANK: dict[Classification, int] = {
    Classification.PUBLIC: 0,
    Classification.INTERNAL: 1,
    Classification.CONFIDENTIAL: 2,
    Classification.REGULATED: 3,
    Classification.MISSION_CRITICAL: 4,
}


class ActionRisk(StrEnum):
    READ = "read"
    ANALYZE = "analyze"
    WRITE_CASE = "write_case"
    EXPORT = "export"
    OPERATIONAL_RECOMMENDATION = "operational_recommendation"


class SubjectContext(StrictModel):
    subject_id: str = Field(min_length=1)
    roles: set[str] = Field(default_factory=set)
    clearance: Classification = Classification.INTERNAL
    compartments: set[str] = Field(default_factory=set)
    coalition: str = Field(min_length=1)
    active_mission_ids: set[str] = Field(default_factory=set)
    break_glass: bool = False


class ResourceContext(StrictModel):
    resource_id: str = Field(min_length=1)
    classification: Classification
    compartments: set[str] = Field(default_factory=set)
    coalition: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    owner_org: str = "ClearGlassInc Artemis"
    pii_fields: set[str] = Field(default_factory=set)


class ToolInvocation(StrictModel):
    tool_name: str = Field(min_length=1)
    action: ActionRisk
    purpose: str = Field(min_length=12)
    arguments: dict[str, Any] = Field(default_factory=dict)
    requires_human_approval: bool = False

    @model_validator(mode="after")
    def high_risk_actions_require_approval_flag(self) -> "ToolInvocation":
        if self.action in {ActionRisk.EXPORT, ActionRisk.OPERATIONAL_RECOMMENDATION} and not self.requires_human_approval:
            raise ValueError("export and operational recommendation actions must declare human approval")
        return self


class PolicyDecision(StrictModel):
    decision: Literal["allow", "deny", "allow_with_human_approval"]
    reasons: list[str]
    obligations: list[str]
    audit_hash: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=sorted)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def evaluate_tool_policy(subject: SubjectContext, resource: ResourceContext, invocation: ToolInvocation) -> PolicyDecision:
    """Evaluate need-to-know, coalition, compartment, and action-risk policy.

    The function fails closed and returns explicit obligations that callers must
    enforce before dispatching a tool. It is safe to run before LLM calls, after
    model planning, and again immediately before execution.
    """

    reasons: list[str] = []
    obligations = ["record immutable audit event", "propagate x-request-id and mission_id"]

    if resource.mission_id not in subject.active_mission_ids:
        reasons.append("subject is not assigned to the resource mission")
    if subject.coalition != resource.coalition:
        reasons.append("coalition boundary mismatch")
    if not resource.compartments.issubset(subject.compartments):
        reasons.append("subject lacks required compartments")
    if CLASSIFICATION_RANK[subject.clearance] < CLASSIFICATION_RANK[resource.classification]:
        reasons.append("subject clearance is below resource classification")
    if invocation.action in {ActionRisk.WRITE_CASE, ActionRisk.EXPORT, ActionRisk.OPERATIONAL_RECOMMENDATION}:
        if "operator" not in subject.roles and "commander" not in subject.roles:
            reasons.append("consequential actions require operator or commander role")
    if invocation.action == ActionRisk.EXPORT and resource.pii_fields:
        obligations.append("apply column-level minimization for pii_fields")
    if subject.break_glass:
        obligations.append("notify security steward and require post-incident review")

    audit_hash = _stable_hash(
        {
            "subject_id": subject.subject_id,
            "resource_id": resource.resource_id,
            "tool_name": invocation.tool_name,
            "action": invocation.action.value,
            "mission_id": resource.mission_id,
            "reasons": reasons,
            "obligations": obligations,
        }
    )

    if reasons and not subject.break_glass:
        return PolicyDecision(decision="deny", reasons=reasons, obligations=obligations, audit_hash=audit_hash)
    if invocation.requires_human_approval or subject.break_glass:
        return PolicyDecision(
            decision="allow_with_human_approval",
            reasons=reasons or ["action is permitted only after explicit human approval"],
            obligations=obligations + ["capture approver_id and approval_ticket before execution"],
            audit_hash=audit_hash,
        )
    return PolicyDecision(decision="allow", reasons=["policy checks passed"], obligations=obligations, audit_hash=audit_hash)
