"""Governed self-improvement controls for ClearGlassInc Artemis.

The loop evaluates prompt, workflow, and routing changes as proposals. It never
mutates production behavior directly; approved deployment remains an Apollo/
human-review concern outside this module.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SignalType(StrEnum):
    OPERATOR_CORRECTION = "operator_correction"
    ALERT_OUTCOME = "alert_outcome"
    QUERY_LOG = "query_log"
    MISSION_RESULT = "mission_result"
    EVAL_RESULT = "eval_result"


class FeedbackSignal(StrictModel):
    signal_id: str = Field(min_length=1)
    signal_type: SignalType
    target_id: str = Field(min_length=1)
    mission_id: str = Field(min_length=1)
    operator_id: str | None = None
    rating: float | None = Field(default=None, ge=0.0, le=1.0)
    correction: str | None = None
    outcome: Literal["true_positive", "false_positive", "duplicate", "stale", "escalated", "unknown"] = "unknown"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalMetrics(StrictModel):
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    unsupported_claim_rate: float = Field(ge=0.0, le=1.0)
    p95_latency_ms: float = Field(ge=0.0)
    policy_denial_rate: float = Field(ge=0.0, le=1.0)
    operator_trust: float = Field(ge=0.0, le=1.0)

    @field_validator("p95_latency_ms")
    @classmethod
    def finite_latency(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("p95_latency_ms must be finite")
        return value


class ChangeProposal(StrictModel):
    proposal_id: str = Field(min_length=1)
    change_type: Literal["prompt", "workflow", "model_routing", "policy"]
    target_version: str = Field(min_length=1)
    candidate_version: str = Field(min_length=1)
    diff: str = Field(min_length=1)
    baseline_metrics: EvalMetrics
    candidate_metrics: EvalMetrics
    affected_missions: list[str] = Field(min_length=1)
    risk_score: float = Field(ge=0.0, le=1.0)
    created_by: Literal["improvement_agent", "human"] = "improvement_agent"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def candidate_must_be_new(self) -> "ChangeProposal":
        if self.target_version == self.candidate_version:
            raise ValueError("candidate_version must differ from target_version")
        return self

    def evidence_hash(self) -> str:
        payload = self.model_dump(mode="json", exclude={"created_at"})
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class ProposalDecision(StrictModel):
    proposal_id: str
    status: Literal["approve_for_human_review", "reject"]
    reasons: list[str]
    evidence_hash: str
    rollback_plan_required: bool = True
    canary_percent: int = Field(default=5, ge=1, le=25)


class FeedbackReadinessReport(StrictModel):
    """Deterministic signal-quality report for building eval sets.

    Artemis treats operator feedback as mission evidence, not as permission for
    autonomous behavior changes. This report makes the data-product boundary
    explicit: enough diverse, recent, high-signal feedback can create an eval
    candidate set, but prompt/workflow/model changes still flow through
    ``ChangeProposal`` and human approval.
    """

    mission_id: str
    signal_count: int
    unique_targets: int
    outcome_counts: dict[str, int]
    average_rating: float | None
    correction_count: int
    ready_for_eval_generation: bool
    blockers: list[str]


class DriftAlert(StrictModel):
    metric_name: str
    baseline_value: float
    candidate_value: float
    relative_change: float
    severity: Literal["watch", "review", "halt"]
    reason: str


class EvalPartition(StrEnum):
    DEVELOPMENT = "development"
    HOLDOUT = "holdout"


class FeedbackEvalCase(StrictModel):
    """De-identified, target-level case derived from mission feedback."""

    case_id: str = Field(pattern=r"^eval_[0-9a-f]{16}$")
    target_id: str = Field(min_length=1)
    partition: EvalPartition
    signal_types: tuple[SignalType, ...] = Field(min_length=1)
    expected_outcomes: tuple[str, ...] = Field(min_length=1)
    corrections: tuple[str, ...] = ()
    source_signal_ids: tuple[str, ...] = Field(min_length=1)


class FeedbackEvalDataset(StrictModel):
    """Immutable manifest for a reproducible, mission-scoped evaluation set."""

    dataset_id: str = Field(pattern=r"^evalset_[0-9a-f]{16}$")
    mission_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    cases: tuple[FeedbackEvalCase, ...] = Field(min_length=1)
    source_signal_count: int = Field(ge=1)
    manifest_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def summarize_feedback_readiness(
    signals: list[FeedbackSignal],
    *,
    mission_id: str,
    min_signals: int = 25,
    min_unique_targets: int = 10,
) -> FeedbackReadinessReport:
    """Summarize whether feedback is strong enough to seed governed evals."""

    mission_signals = [signal for signal in signals if signal.mission_id == mission_id]
    outcome_counts: dict[str, int] = {}
    ratings: list[float] = []
    correction_count = 0
    unique_targets = {signal.target_id for signal in mission_signals}

    for signal in mission_signals:
        outcome_counts[signal.outcome] = outcome_counts.get(signal.outcome, 0) + 1
        if signal.rating is not None:
            ratings.append(signal.rating)
        if signal.correction:
            correction_count += 1

    blockers: list[str] = []
    if len(mission_signals) < min_signals:
        blockers.append(f"requires at least {min_signals} mission-scoped feedback signals")
    if len(unique_targets) < min_unique_targets:
        blockers.append(f"requires at least {min_unique_targets} unique targets to avoid overfitting")
    if correction_count == 0 and not {"false_positive", "stale", "duplicate"}.intersection(outcome_counts):
        blockers.append("requires corrections or negative outcomes for discriminative eval cases")

    average_rating = round(sum(ratings) / len(ratings), 4) if ratings else None
    return FeedbackReadinessReport(
        mission_id=mission_id,
        signal_count=len(mission_signals),
        unique_targets=len(unique_targets),
        outcome_counts=outcome_counts,
        average_rating=average_rating,
        correction_count=correction_count,
        ready_for_eval_generation=not blockers,
        blockers=blockers,
    )


def generate_feedback_eval_dataset(
    signals: list[FeedbackSignal],
    *,
    mission_id: str,
    version: str,
    holdout_fraction: float = 0.2,
) -> FeedbackEvalDataset:
    """Build a deterministic eval manifest after the feedback quality gate passes.

    Signals are grouped by target to prevent repeated feedback from producing
    duplicate cases. Operator identities and arbitrary metadata are deliberately
    excluded. Partition assignment is hash-based and then cardinality-bounded so
    identical inputs always produce the same non-empty holdout set.
    """

    if not 0.1 <= holdout_fraction <= 0.5:
        raise ValueError("holdout_fraction must be between 0.1 and 0.5")
    readiness = summarize_feedback_readiness(signals, mission_id=mission_id)
    if not readiness.ready_for_eval_generation:
        raise ValueError(f"feedback is not ready for eval generation: {'; '.join(readiness.blockers)}")

    mission_signals = sorted(
        (signal for signal in signals if signal.mission_id == mission_id),
        key=lambda signal: (signal.target_id, signal.signal_id),
    )
    grouped: dict[str, list[FeedbackSignal]] = defaultdict(list)
    for signal in mission_signals:
        grouped[signal.target_id].append(signal)

    ranked_targets = sorted(
        grouped,
        key=lambda target_id: hashlib.sha256(f"{mission_id}:{version}:{target_id}".encode()).hexdigest(),
    )
    holdout_count = max(1, round(len(ranked_targets) * holdout_fraction))
    holdout_targets = set(ranked_targets[:holdout_count])
    cases: list[FeedbackEvalCase] = []
    for target_id in sorted(grouped):
        target_signals = grouped[target_id]
        case_digest = hashlib.sha256(f"{mission_id}:{version}:{target_id}".encode()).hexdigest()
        cases.append(
            FeedbackEvalCase(
                case_id=f"eval_{case_digest[:16]}",
                target_id=target_id,
                partition=EvalPartition.HOLDOUT if target_id in holdout_targets else EvalPartition.DEVELOPMENT,
                signal_types=tuple(sorted({signal.signal_type for signal in target_signals}, key=str)),
                expected_outcomes=tuple(sorted({signal.outcome for signal in target_signals})),
                corrections=tuple(sorted({signal.correction for signal in target_signals if signal.correction})),
                source_signal_ids=tuple(signal.signal_id for signal in target_signals),
            )
        )

    manifest = {
        "mission_id": mission_id,
        "version": version,
        "source_signal_count": len(mission_signals),
        "cases": [case.model_dump(mode="json") for case in cases],
    }
    digest = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return FeedbackEvalDataset(
        dataset_id=f"evalset_{digest[:16]}",
        mission_id=mission_id,
        version=version,
        cases=tuple(cases),
        source_signal_count=len(mission_signals),
        manifest_hash=f"sha256:{digest}",
    )


def detect_metric_drift(
    baseline: EvalMetrics,
    candidate: EvalMetrics,
    *,
    halt_threshold: float = 0.20,
    review_threshold: float = 0.10,
) -> list[DriftAlert]:
    """Create reviewable drift alerts from baseline and candidate eval metrics."""

    alerts: list[DriftAlert] = []
    metric_directions = {
        "precision": "higher_is_better",
        "recall": "higher_is_better",
        "unsupported_claim_rate": "lower_is_better",
        "p95_latency_ms": "lower_is_better",
        "policy_denial_rate": "lower_is_better",
        "operator_trust": "higher_is_better",
    }

    for metric_name, direction in metric_directions.items():
        base_value = float(getattr(baseline, metric_name))
        cand_value = float(getattr(candidate, metric_name))
        denominator = base_value if base_value != 0 else 1.0
        relative_change = (cand_value - base_value) / denominator
        harmful_change = -relative_change if direction == "higher_is_better" else relative_change

        if harmful_change >= halt_threshold:
            severity: Literal["watch", "review", "halt"] = "halt"
        elif harmful_change >= review_threshold:
            severity = "review"
        elif abs(relative_change) >= review_threshold:
            severity = "watch"
        else:
            continue

        alerts.append(
            DriftAlert(
                metric_name=metric_name,
                baseline_value=base_value,
                candidate_value=cand_value,
                relative_change=round(relative_change, 6),
                severity=severity,
                reason=f"{metric_name} changed {relative_change:.1%} versus governed baseline",
            )
        )

    return alerts


def evaluate_change_proposal(proposal: ChangeProposal) -> ProposalDecision:
    """Fail-closed gate for Artemis self-improvement proposals.

    This deterministic policy is intentionally conservative: a candidate must
    improve at least one quality metric, avoid regressions beyond tolerance,
    stay under risk limits, and remain queued for human approval rather than
    directly deploying itself.
    """

    reasons: list[str] = []
    base = proposal.baseline_metrics
    cand = proposal.candidate_metrics

    if proposal.created_by != "improvement_agent":
        reasons.append("proposal source must be improvement_agent for automated gate")
    if proposal.change_type == "policy":
        reasons.append("policy changes require manual security-governance review")
    if proposal.risk_score > 0.35:
        reasons.append("risk score exceeds governed self-improvement threshold")
    if cand.unsupported_claim_rate > base.unsupported_claim_rate:
        reasons.append("unsupported claim rate regressed")
    if cand.precision + 0.01 < base.precision:
        reasons.append("precision regressed beyond 1 percentage point")
    if cand.recall + 0.02 < base.recall:
        reasons.append("recall regressed beyond 2 percentage points")
    if cand.p95_latency_ms > base.p95_latency_ms * 1.10:
        reasons.append("p95 latency regressed beyond 10 percent")
    if cand.policy_denial_rate > base.policy_denial_rate + 0.02:
        reasons.append("policy denial rate regressed beyond 2 percentage points")
    if cand.operator_trust + 0.01 < base.operator_trust:
        reasons.append("operator trust regressed beyond 1 percentage point")

    quality_improved = (
        cand.precision > base.precision
        or cand.recall > base.recall
        or cand.unsupported_claim_rate < base.unsupported_claim_rate
        or cand.operator_trust > base.operator_trust
    )
    if not quality_improved:
        reasons.append("candidate does not improve governed quality metrics")

    return ProposalDecision(
        proposal_id=proposal.proposal_id,
        status="reject" if reasons else "approve_for_human_review",
        reasons=reasons or ["candidate passed deterministic gate; human approval and Apollo canary still required"],
        evidence_hash=proposal.evidence_hash(),
    )
