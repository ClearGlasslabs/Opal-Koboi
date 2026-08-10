"""Evidence-graph primitives for ClearGlassInc Artemis AEGIS Federal.

The module deliberately evaluates evidence, not legal compliance.  A deployment
must load a counsel-approved control catalogue.  Deterministic scoring makes the
result reproducible and keeps model-generated assertions out of the trust path.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Framework(StrEnum):
    CCSPA = "CCSPA"
    CYBER_CENTRE = "CYBER_CENTRE"
    OSFI_B10 = "OSFI_B-10"
    OSFI_B13 = "OSFI_B-13"
    OSFI_E21 = "OSFI_E-21"
    AI_RISK = "AI_RISK"


class EvidenceStatus(StrEnum):
    VERIFIED = "verified"
    STALE = "stale"
    MISSING = "missing"
    DISPUTED = "disputed"


class FindingSeverity(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class Requirement(StrictModel):
    requirement_id: str = Field(min_length=1)
    framework: Framework
    citation: str = Field(min_length=1)
    title: str = Field(min_length=1)
    control_ids: frozenset[str] = Field(min_length=1)
    counsel_approved: bool = False


class Control(StrictModel):
    control_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    owner_id: str = Field(min_length=1)
    system_ids: frozenset[str] = Field(min_length=1)
    evidence_ids: frozenset[str] = Field(min_length=1)
    critical: bool = False


class Evidence(StrictModel):
    evidence_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_uri: str = Field(min_length=1)
    content_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    collected_at: datetime
    valid_until: datetime
    status: EvidenceStatus = EvidenceStatus.VERIFIED
    classification: str = Field(min_length=1)
    releasable_to: frozenset[str] = frozenset()

    @model_validator(mode="after")
    def temporal_order(self) -> "Evidence":
        if self.valid_until <= self.collected_at:
            raise ValueError("valid_until must be after collected_at")
        return self


class Finding(StrictModel):
    finding_id: str
    requirement_id: str
    control_id: str
    severity: FindingSeverity
    reason: str
    owner_id: str


class ControlResult(StrictModel):
    control_id: str
    verified: int
    expected: int
    coverage: float = Field(ge=0, le=1)
    status: EvidenceStatus
    evidence_ids: tuple[str, ...]


class AssuranceReport(StrictModel):
    tenant_id: str
    mission_id: str
    framework_versions: dict[Framework, str]
    generated_at: datetime
    results: tuple[ControlResult, ...]
    findings: tuple[Finding, ...]
    coverage: float = Field(ge=0, le=1)
    report_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    disclaimer: str = "Evidence sufficiency assessment; not a legal compliance determination."


class BundleRequest(StrictModel):
    tenant_id: str
    mission_id: str
    requested_by: str
    requirement_ids: frozenset[str] = Field(min_length=1)
    audience: str = Field(min_length=1)
    approval_ids: tuple[str, ...] = ()


class EvidenceBundle(StrictModel):
    manifest_id: str
    requirement_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    report_hash: str
    approved_by: tuple[str, ...]
    export_allowed: bool


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(encoded.encode()).hexdigest()}"


def evaluate_assurance(
    *,
    tenant_id: str,
    mission_id: str,
    requirements: list[Requirement],
    controls: list[Control],
    evidence: list[Evidence],
    framework_versions: dict[Framework, str],
    as_of: datetime | None = None,
) -> AssuranceReport:
    """Resolve Requirement → Control → Evidence and emit reproducible gaps."""

    now = as_of or datetime.now(timezone.utc)
    if any(not requirement.counsel_approved for requirement in requirements):
        raise ValueError("every regulatory requirement must be counsel-approved")
    control_index = {control.control_id: control for control in controls}
    evidence_index = {
        item.evidence_id: item
        for item in evidence
        if item.tenant_id == tenant_id and item.mission_id == mission_id
    }
    results: list[ControlResult] = []
    findings: list[Finding] = []

    for control in sorted(controls, key=lambda item: item.control_id):
        items = [evidence_index[item_id] for item_id in sorted(control.evidence_ids) if item_id in evidence_index]
        verified = [item for item in items if item.status == EvidenceStatus.VERIFIED and item.valid_until > now]
        if len(verified) == len(control.evidence_ids):
            status = EvidenceStatus.VERIFIED
        elif any(item.status == EvidenceStatus.DISPUTED for item in items):
            status = EvidenceStatus.DISPUTED
        elif items:
            status = EvidenceStatus.STALE
        else:
            status = EvidenceStatus.MISSING
        results.append(ControlResult(
            control_id=control.control_id,
            verified=len(verified),
            expected=len(control.evidence_ids),
            coverage=len(verified) / len(control.evidence_ids),
            status=status,
            evidence_ids=tuple(item.evidence_id for item in verified),
        ))

    result_index = {result.control_id: result for result in results}
    for requirement in sorted(requirements, key=lambda item: item.requirement_id):
        for control_id in sorted(requirement.control_ids):
            if control_id not in control_index:
                raise ValueError(f"requirement {requirement.requirement_id} references unknown control {control_id}")
            result = result_index[control_id]
            if result.status != EvidenceStatus.VERIFIED:
                control = control_index[control_id]
                severity = FindingSeverity.CRITICAL if control.critical and result.coverage == 0 else (
                    FindingSeverity.HIGH if control.critical else FindingSeverity.MODERATE
                )
                finding_id = _digest([requirement.requirement_id, control_id, result.status])[-16:]
                findings.append(Finding(
                    finding_id=f"finding_{finding_id}", requirement_id=requirement.requirement_id,
                    control_id=control_id, severity=severity,
                    reason=f"control evidence is {result.status}; verified {result.verified}/{result.expected}",
                    owner_id=control.owner_id,
                ))

    coverage = sum(result.coverage for result in results) / len(results) if results else 0.0
    generated_at = now
    report_payload = {
        "tenant_id": tenant_id, "mission_id": mission_id,
        "framework_versions": {key.value: value for key, value in framework_versions.items()},
        "generated_at": generated_at.isoformat(),
        "results": [result.model_dump(mode="json") for result in results],
        "findings": [finding.model_dump(mode="json") for finding in findings],
        "coverage": coverage,
    }
    return AssuranceReport(
        tenant_id=tenant_id,
        mission_id=mission_id,
        framework_versions=framework_versions,
        generated_at=generated_at,
        results=tuple(results),
        findings=tuple(findings),
        coverage=coverage,
        report_hash=_digest(report_payload),
    )


def prepare_evidence_bundle(
    request: BundleRequest,
    report: AssuranceReport,
    requirements: list[Requirement],
) -> EvidenceBundle:
    """Prepare a manifest; external export stays closed without two approvers."""

    if (request.tenant_id, request.mission_id) != (report.tenant_id, report.mission_id):
        raise ValueError("bundle request scope does not match assurance report")
    requirement_index = {item.requirement_id: item for item in requirements}
    unknown = request.requirement_ids - requirement_index.keys()
    if unknown:
        raise ValueError(f"unknown requirements: {sorted(unknown)}")
    control_ids = {cid for rid in request.requirement_ids for cid in requirement_index[rid].control_ids}
    evidence_ids = sorted({eid for result in report.results if result.control_id in control_ids for eid in result.evidence_ids})
    distinct_approvers = tuple(dict.fromkeys(request.approval_ids))
    payload = [request.tenant_id, request.mission_id, sorted(request.requirement_ids), evidence_ids, report.report_hash]
    return EvidenceBundle(
        manifest_id=f"bundle_{_digest(payload)[-16:]}", requirement_ids=tuple(sorted(request.requirement_ids)),
        evidence_ids=tuple(evidence_ids), report_hash=report.report_hash,
        approved_by=distinct_approvers, export_allowed=len(distinct_approvers) >= 2,
    )
