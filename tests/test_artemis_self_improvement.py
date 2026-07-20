from __future__ import annotations

import pytest

from intelligence.artemis_self_improvement import (
    ChangeProposal,
    EvalMetrics,
    FeedbackSignal,
    SignalType,
    detect_metric_drift,
    evaluate_change_proposal,
    summarize_feedback_readiness,
)


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


def test_summarizes_feedback_readiness_for_eval_generation():
    signals = [
        FeedbackSignal(
            signal_id=f"sig-{index}",
            signal_type=SignalType.OPERATOR_CORRECTION,
            target_id=f"alert-{index % 12}",
            mission_id="mis_northstar",
            rating=0.8,
            correction="downgrade severity" if index == 3 else None,
            outcome="false_positive" if index == 3 else "true_positive",
        )
        for index in range(25)
    ]

    report = summarize_feedback_readiness(signals, mission_id="mis_northstar")

    assert report.ready_for_eval_generation is True
    assert report.signal_count == 25
    assert report.unique_targets == 12
    assert report.average_rating == 0.8
    assert report.outcome_counts["false_positive"] == 1


def test_feedback_readiness_blocks_sparse_or_overfit_signals():
    signals = [
        FeedbackSignal(
            signal_id="sig-1",
            signal_type=SignalType.ALERT_OUTCOME,
            target_id="alert-1",
            mission_id="mis_northstar",
            outcome="true_positive",
        )
    ]

    report = summarize_feedback_readiness(signals, mission_id="mis_northstar")

    assert report.ready_for_eval_generation is False
    assert "requires at least 25 mission-scoped feedback signals" in report.blockers
    assert "requires at least 10 unique targets to avoid overfitting" in report.blockers


def test_detect_metric_drift_creates_reviewable_alerts():
    alerts = detect_metric_drift(
        metrics(),
        metrics(precision=0.65, p95_latency_ms=1030.0, unsupported_claim_rate=0.03),
    )

    alert_by_metric = {alert.metric_name: alert for alert in alerts}
    assert alert_by_metric["precision"].severity == "halt"
    assert alert_by_metric["p95_latency_ms"].severity == "review"
    assert alert_by_metric["unsupported_claim_rate"].severity == "watch"
