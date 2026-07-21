import pytest

from intelligence.artemis_incident_control import (
    IncidentContext,
    IncidentEvidence,
    LifecycleStage,
    RecoveryAction,
    classify_incident,
    evaluate_recovery_action,
)


def evidence(**overrides):
    values = {
        "evidence_id": "ev-1",
        "source": "otel.alert.policy-denial-rate",
        "signal_type": "policy_denial_spike",
        "confidence": 0.91,
        "content_hash": "sha256:" + "a" * 64,
    }
    values.update(overrides)
    return IncidentEvidence(**values)


def context(**overrides):
    ev = [evidence()]
    values = {
        "incident_id": "inc-001",
        "tenant_id": "tenant-clearglass",
        "mission_id": "mis-northstar",
        "current_stage": LifecycleStage.CONTAIN,
        "severity": classify_incident(ev, affected_asset_count=3),
        "evidence": ev,
        "affected_assets": {"svc-api", "queue-ingest"},
    }
    values.update(overrides)
    return IncidentContext(**values)


def action(**overrides):
    values = {
        "action_id": "act-contain-1",
        "action_type": "containment",
        "stage": LifecycleStage.CONTAIN,
        "scope": {"svc-api"},
        "idempotency_key": "inc-001:contain:svc-api",
        "timeout_seconds": 120,
        "max_attempts": 3,
        "blast_radius_ceiling": 1,
        "rollback_strategy": "restore previous routing and replay dead-lettered events",
        "requires_human_approval": True,
        "approved_by": "usr-commander",
        "approval_ticket": "INC-001-APPROVAL",
    }
    values.update(overrides)
    return RecoveryAction(**values)


def test_classifies_incident_from_validated_evidence():
    assert classify_incident([evidence(confidence=0.95)], affected_asset_count=30).value == "critical"
    assert classify_incident([evidence(confidence=0.5)], affected_asset_count=1).value == "medium"


def test_allows_bounded_high_impact_action_with_human_approval():
    decision = evaluate_recovery_action(context(), action())

    assert decision.decision == "allow"
    assert decision.receipt_hash
    assert "append tamper-evident audit receipt" in decision.obligations


def test_denies_when_kill_switch_or_scope_violate_controls():
    decision = evaluate_recovery_action(
        context(),
        action(kill_switch_engaged=True, scope={"svc-api", "unknown-service"}, blast_radius_ceiling=1),
    )

    assert decision.decision == "deny"
    assert "automation kill switch is engaged" in decision.reasons
    assert "action scope exceeds blast-radius ceiling" in decision.reasons
    assert "action scope includes assets outside incident blast radius" in decision.reasons


def test_high_impact_actions_require_approval_metadata():
    with pytest.raises(ValueError, match="high-impact actions require"):
        action(requires_human_approval=True, approved_by=None)
