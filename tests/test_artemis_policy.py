import pytest

from intelligence.artemis_policy import (
    ActionRisk,
    Classification,
    ResourceContext,
    SubjectContext,
    ToolInvocation,
    evaluate_tool_policy,
)


def subject(**overrides) -> SubjectContext:
    values = {
        "subject_id": "usr_analyst_01",
        "roles": {"analyst", "operator"},
        "clearance": Classification.REGULATED,
        "compartments": {"northstar", "supply-chain"},
        "coalition": "clear-glass",
        "active_mission_ids": {"mis_northstar"},
    }
    values.update(overrides)
    return SubjectContext(**values)


def resource(**overrides) -> ResourceContext:
    values = {
        "resource_id": "ent_supplier_123",
        "classification": Classification.CONFIDENTIAL,
        "compartments": {"northstar"},
        "coalition": "clear-glass",
        "mission_id": "mis_northstar",
    }
    values.update(overrides)
    return ResourceContext(**values)


def invocation(**overrides) -> ToolInvocation:
    values = {
        "tool_name": "ontology.search_entities",
        "action": ActionRisk.ANALYZE,
        "purpose": "correlate mission-scoped supplier risk signals",
    }
    values.update(overrides)
    return ToolInvocation(**values)


def test_allows_mission_scoped_analysis_with_audit_obligations():
    decision = evaluate_tool_policy(subject(), resource(), invocation())

    assert decision.decision == "allow"
    assert decision.audit_hash
    assert "record immutable audit event" in decision.obligations


def test_denies_cross_coalition_or_unassigned_mission_access():
    decision = evaluate_tool_policy(
        subject(active_mission_ids={"mis_other"}),
        resource(coalition="partner-force"),
        invocation(),
    )

    assert decision.decision == "deny"
    assert "subject is not assigned to the resource mission" in decision.reasons
    assert "coalition boundary mismatch" in decision.reasons


def test_operational_recommendation_requires_human_approval():
    decision = evaluate_tool_policy(
        subject(),
        resource(classification=Classification.REGULATED),
        invocation(
            tool_name="case.prepare_action_package",
            action=ActionRisk.OPERATIONAL_RECOMMENDATION,
            purpose="prepare commander review package with cited evidence",
            requires_human_approval=True,
        ),
    )

    assert decision.decision == "allow_with_human_approval"
    assert "capture approver_id and approval_ticket before execution" in decision.obligations


def test_export_requires_approval_flag_at_model_boundary():
    with pytest.raises(ValueError, match="must declare human approval"):
        invocation(action=ActionRisk.EXPORT, purpose="export minimized partner intelligence package")
