"""Apollo-style deployment execution gate for ClearGlassInc Artemis.

This module turns approved self-improvement proposals into deterministic deployment
execution plans. It does not contact Apollo or mutate runtime state; callers hand
the returned plan to an approved deployment controller after recording the audit
artifact.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from intelligence.artemis_self_improvement import ChangeProposal, ProposalDecision


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DeploymentRing(StrEnum):
    SHADOW = "shadow"
    CANARY = "canary"
    MISSION = "mission"


class DeploymentArtifact(StrictModel):
    artifact_id: str = Field(min_length=1)
    artifact_type: Literal["prompt", "workflow", "model_routing"]
    version: str = Field(min_length=1)
    digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    rollback_version: str = Field(min_length=1)
    rollback_digest: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class DeploymentRequest(StrictModel):
    request_id: str = Field(min_length=1)
    proposal: ChangeProposal
    decision: ProposalDecision
    artifact: DeploymentArtifact
    approver_id: str = Field(min_length=1)
    approval_ticket: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    target_ring: DeploymentRing = DeploymentRing.CANARY
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_request_consistency(self) -> "DeploymentRequest":
        if self.decision.proposal_id != self.proposal.proposal_id:
            raise ValueError("decision must reference the same proposal")
        if self.artifact.artifact_type != self.proposal.change_type:
            raise ValueError("artifact type must match proposal change type")
        if self.artifact.version != self.proposal.candidate_version:
            raise ValueError("artifact version must match candidate version")
        if self.artifact.rollback_version != self.proposal.target_version:
            raise ValueError("rollback version must match target version")
        return self


class DeploymentStep(StrictModel):
    name: str
    action: Literal["verify", "deploy", "observe", "rollback"]
    command: str
    success_criteria: list[str]


class DeploymentPlan(StrictModel):
    plan_id: str
    request_id: str
    proposal_id: str
    ring: DeploymentRing
    canary_percent: int = Field(ge=1, le=25)
    artifact_digest: str
    rollback_digest: str
    approval_ticket: str
    approver_id: str
    policy_version: str
    steps: list[DeploymentStep] = Field(min_length=1)
    audit_hash: str


def _stable_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_deployment_plan(request: DeploymentRequest) -> DeploymentPlan:
    """Build a fail-closed Apollo handoff plan for an approved proposal."""

    if request.decision.status != "approve_for_human_review":
        raise ValueError("deployment requires a proposal approved for human review")
    if request.proposal.change_type == "policy":
        raise ValueError("policy deployments require the manual security-governance release path")
    if not request.decision.rollback_plan_required:
        raise ValueError("rollback plan is mandatory for self-improvement deployments")

    base_payload = {
        "request_id": request.request_id,
        "proposal_id": request.proposal.proposal_id,
        "candidate_version": request.proposal.candidate_version,
        "artifact_digest": request.artifact.digest,
        "rollback_digest": request.artifact.rollback_digest,
        "approval_ticket": request.approval_ticket,
        "approver_id": request.approver_id,
        "policy_version": request.policy_version,
        "ring": request.target_ring.value,
    }
    audit_hash = _stable_hash(base_payload)
    plan_id = f"deploy_{audit_hash[:16]}"

    return DeploymentPlan(
        plan_id=plan_id,
        request_id=request.request_id,
        proposal_id=request.proposal.proposal_id,
        ring=request.target_ring,
        canary_percent=request.decision.canary_percent,
        artifact_digest=request.artifact.digest,
        rollback_digest=request.artifact.rollback_digest,
        approval_ticket=request.approval_ticket,
        approver_id=request.approver_id,
        policy_version=request.policy_version,
        audit_hash=audit_hash,
        steps=[
            DeploymentStep(
                name="verify-signed-artifact",
                action="verify",
                command=f"apollo artifact verify {request.artifact.artifact_id} --digest {request.artifact.digest}",
                success_criteria=["signature chains to approved ClearGlassInc Artemis release key", "SBOM and provenance are attached"],
            ),
            DeploymentStep(
                name="deploy-canary-ring",
                action="deploy",
                command=(
                    f"apollo deploy {request.artifact.artifact_id} --ring {request.target_ring.value} "
                    f"--percent {request.decision.canary_percent} --policy {request.policy_version}"
                ),
                success_criteria=["health checks pass", "human approval gates remain enabled", "policy denials do not spike"],
            ),
            DeploymentStep(
                name="observe-mission-health",
                action="observe",
                command=f"apollo observe {plan_id} --metrics precision,recall,p95_latency_ms,operator_trust",
                success_criteria=["no halt drift alerts", "operator override rate within baseline", "p95 latency within SLO"],
            ),
            DeploymentStep(
                name="rollback-on-regression",
                action="rollback",
                command=(
                    f"apollo rollback {request.artifact.artifact_id} --to {request.artifact.rollback_version} "
                    f"--digest {request.artifact.rollback_digest}"
                ),
                success_criteria=["previous signed version restored", "failed deployment preserved for audit"],
            ),
        ],
    )
