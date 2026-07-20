from __future__ import annotations

import pytest

from intelligence.artemis_self_improvement import ChangeProposal, EvalMetrics, evaluate_change_proposal


def metrics(**overrides) -> EvalMetrics:
    values = {
        "precision": 0.82,
        "recall": 0.74,
        "unsupported_claim_rate": 0.06,
        "p95_latency_ms": 900.0,
        "policy_denial_rate": 0.03,
        "operator_trust": 0.78,
    }
    values.update(overrides)
    return EvalMetrics(**values)


def proposal(**overrides) -> ChangeProposal:
    values = {
        "proposal_id": "cp_prompt_001",
        "change_type": "prompt",
        "target_version": "triage-v7",
        "candidate_version": "triage-v8",
        "diff": "- vague severity rubric\n+ evidence-weighted severity rubric",
        "baseline_metrics": metrics(),
        "candidate_metrics": metrics(precision=0.85, unsupported_claim_rate=0.04, operator_trust=0.80),
        "affected_missions": ["mis_northstar"],
        "risk_score": 0.2,
    }
    values.update(overrides)
    return ChangeProposal(**values)


def test_safe_candidate_is_only_approved_for_human_review():
    decision = evaluate_change_proposal(proposal())
    assert decision.status == "approve_for_human_review"
    assert decision.rollback_plan_required is True
    assert decision.canary_percent == 5
    assert decision.evidence_hash
    assert "human approval" in decision.reasons[0]


def test_rejects_unsupported_claim_regression():
    decision = evaluate_change_proposal(proposal(candidate_metrics=metrics(unsupported_claim_rate=0.07)))
    assert decision.status == "reject"
    assert "unsupported claim rate regressed" in decision.reasons


def test_rejects_policy_denial_regression():
    decision = evaluate_change_proposal(
        proposal(candidate_metrics=metrics(precision=0.86, policy_denial_rate=0.061))
    )
    assert decision.status == "reject"
    assert "policy denial rate regressed beyond 2 percentage points" in decision.reasons


def test_rejects_high_risk_or_policy_changes():
    decision = evaluate_change_proposal(proposal(change_type="policy", risk_score=0.5))
    assert decision.status == "reject"
    assert "policy changes require manual security-governance review" in decision.reasons
    assert "risk score exceeds governed self-improvement threshold" in decision.reasons


def test_rejects_no_op_candidate_version():
    with pytest.raises(ValueError, match="candidate_version must differ"):
        proposal(candidate_version="triage-v7")
