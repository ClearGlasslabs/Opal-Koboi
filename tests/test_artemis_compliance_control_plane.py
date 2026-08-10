from datetime import datetime, timedelta, timezone

import pytest

from intelligence.artemis_compliance_control_plane import (
    BundleRequest,
    Control,
    Evidence,
    EvidenceStatus,
    Framework,
    Requirement,
    evaluate_assurance,
    prepare_evidence_bundle,
)

NOW = datetime(2026, 8, 10, tzinfo=timezone.utc)


def evidence(evidence_id: str, *, expired: bool = False, mission_id: str = "mission-c8") -> Evidence:
    return Evidence(
        evidence_id=evidence_id, tenant_id="tenant-ca", mission_id=mission_id,
        source="azure", source_uri=f"foundry://evidence/{evidence_id}",
        content_hash="sha256:" + "a" * 64, collected_at=NOW - timedelta(days=2),
        valid_until=NOW - timedelta(days=1) if expired else NOW + timedelta(days=30),
        status=EvidenceStatus.VERIFIED, classification="PROTECTED B",
    )


def catalogue():
    controls = [
        Control(control_id="IAM-01", title="MFA coverage", owner_id="ciso", system_ids={"azure"}, evidence_ids={"ev-mfa"}, critical=True),
        Control(control_id="TPRM-01", title="Vendor assurance", owner_id="procurement", system_ids={"vendors"}, evidence_ids={"ev-vendor"}),
    ]
    requirements = [
        Requirement(requirement_id="CCSPA-SCR-01", framework=Framework.CCSPA, citation="counsel-map:2026.1:§x", title="Supply-chain risk", control_ids={"TPRM-01"}, counsel_approved=True),
        Requirement(requirement_id="B13-IAM-01", framework=Framework.OSFI_B13, citation="counsel-map:2026.1:B13", title="Identity safeguards", control_ids={"IAM-01"}, counsel_approved=True),
    ]
    return requirements, controls


def test_builds_deterministic_evidence_graph_report_and_findings():
    requirements, controls = catalogue()
    report = evaluate_assurance(
        tenant_id="tenant-ca", mission_id="mission-c8", requirements=requirements,
        controls=controls, evidence=[evidence("ev-mfa"), evidence("ev-vendor", expired=True)],
        framework_versions={Framework.CCSPA: "counsel-map-2026.1", Framework.OSFI_B13: "2022-11"}, as_of=NOW,
    )
    assert report.coverage == 0.5
    assert report.results[0].status == EvidenceStatus.VERIFIED
    assert report.results[1].status == EvidenceStatus.STALE
    assert report.findings[0].owner_id == "procurement"
    assert report.report_hash.startswith("sha256:")


def test_rejects_unapproved_regulatory_interpretation():
    requirements, controls = catalogue()
    requirements[0] = requirements[0].model_copy(update={"counsel_approved": False})
    with pytest.raises(ValueError, match="counsel-approved"):
        evaluate_assurance(tenant_id="tenant-ca", mission_id="mission-c8", requirements=requirements, controls=controls, evidence=[], framework_versions={}, as_of=NOW)


def test_bundle_requires_two_distinct_approvers_for_export():
    requirements, controls = catalogue()
    report = evaluate_assurance(tenant_id="tenant-ca", mission_id="mission-c8", requirements=requirements, controls=controls, evidence=[evidence("ev-mfa"), evidence("ev-vendor")], framework_versions={Framework.CCSPA: "2026.1"}, as_of=NOW)
    request = BundleRequest(tenant_id="tenant-ca", mission_id="mission-c8", requested_by="analyst", requirement_ids={"CCSPA-SCR-01"}, audience="regulator", approval_ids=("legal", "ciso"))
    bundle = prepare_evidence_bundle(request, report, requirements)
    assert bundle.export_allowed is True
    assert bundle.evidence_ids == ("ev-vendor",)
    assert prepare_evidence_bundle(request.model_copy(update={"approval_ids": ("legal", "legal")}), report, requirements).export_allowed is False


def test_ignores_cross_mission_evidence():
    requirements, controls = catalogue()
    report = evaluate_assurance(tenant_id="tenant-ca", mission_id="mission-c8", requirements=requirements, controls=controls, evidence=[evidence("ev-mfa", mission_id="other"), evidence("ev-vendor", mission_id="other")], framework_versions={Framework.CCSPA: "2026.1"}, as_of=NOW)
    assert report.coverage == 0
    assert len(report.findings) == 2
