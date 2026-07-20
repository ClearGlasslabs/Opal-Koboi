import pytest

from intelligence.artemis_deploy_execute import DeploymentArtifact, DeploymentRequest, build_deployment_plan
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


def approved_proposal() -> ChangeProposal:
    return ChangeProposal(
        proposal_id="cp_workflow_042",
        change_type="workflow",
        target_version="triage-flow-v3",
        candidate_version="triage-flow-v4",
        diff="+ require second-source caveat before high-confidence recommendation",
        baseline_metrics=metrics(),
        candidate_metrics=metrics(precision=0.86, unsupported_claim_rate=0.04, operator_trust=0.81),
        affected_missions=["mis_northstar"],
        risk_score=0.18,
    )


def artifact() -> DeploymentArtifact:
    return DeploymentArtifact(
        artifact_id="art_workflow_triage_v4",
        artifact_type="workflow",
        version="triage-flow-v4",
        digest="sha256:" + "a" * 64,
        rollback_version="triage-flow-v3",
        rollback_digest="sha256:" + "b" * 64,
    )


def test_build_deployment_plan_requires_human_review_approval():
    proposal = approved_proposal()
    decision = evaluate_change_proposal(proposal)
    request = DeploymentRequest(
        request_id="dep-001",
        proposal=proposal,
        decision=decision,
        artifact=artifact(),
        approver_id="usr_eval_steward",
        approval_ticket="GOV-2040-17",
        policy_version="policy-v12",
    )

    plan = build_deployment_plan(request)

    assert plan.plan_id.startswith("deploy_")
    assert plan.canary_percent == 5
    assert plan.steps[0].action == "verify"
    assert plan.steps[1].command.startswith("apollo deploy art_workflow_triage_v4")
    assert plan.steps[-1].action == "rollback"
    assert plan.audit_hash


def test_rejects_unapproved_deployment_request():
    proposal = approved_proposal()
    rejected = evaluate_change_proposal(proposal.model_copy(update={"risk_score": 0.9}))
    request = DeploymentRequest(
        request_id="dep-002",
        proposal=proposal,
        decision=rejected,
        artifact=artifact(),
        approver_id="usr_eval_steward",
        approval_ticket="GOV-2040-18",
        policy_version="policy-v12",
    )

    with pytest.raises(ValueError, match="approved for human review"):
        build_deployment_plan(request)


def test_rejects_artifact_version_mismatch():
    proposal = approved_proposal()
    decision = evaluate_change_proposal(proposal)
    bad_artifact = artifact().model_copy(update={"version": "triage-flow-v5"})

    with pytest.raises(ValueError, match="artifact version"):
        DeploymentRequest(
            request_id="dep-003",
            proposal=proposal,
            decision=decision,
            artifact=bad_artifact,
            approver_id="usr_eval_steward",
            approval_ticket="GOV-2040-19",
            policy_version="policy-v12",
        )
