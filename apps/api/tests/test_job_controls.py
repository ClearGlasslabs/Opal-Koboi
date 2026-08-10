from __future__ import annotations

import pytest

from app.core.feature_flags import Capability, FeatureFlags, SAFE_DEFAULT_FLAGS
from app.core.job_registry import JOB_REGISTRY, JobDefinition, JobState, RetryPolicy, Trigger
from app.core.job_runtime import JobRuntime


def test_all_sensitive_capabilities_fail_closed_and_snapshots_are_immutable():
    assert all(not SAFE_DEFAULT_FLAGS.enabled(capability) for capability in Capability)
    with pytest.raises(TypeError):
        SAFE_DEFAULT_FLAGS.snapshot()[Capability.AI] = True
    assert not FeatureFlags({"ai": "true"}).enabled(Capability.AI)


def test_registry_rejects_incomplete_lifecycle_and_duplicate_names():
    with pytest.raises(ValueError, match="success and failure"):
        JobDefinition("bad", "purpose", "owner", Trigger.MANUAL, frozenset({JobState.LOADING}), None, 1, RetryPolicy(1, ()), True, 1, True, "revert")
    job = JOB_REGISTRY.get("threat-model-analysis")
    assert job.owner and job.audit_required and job.idempotency_required
    assert JobState.DEAD_LETTERED in job.lifecycle


def test_disabled_job_never_calls_operation_and_emits_metric_and_audit():
    audit = []
    runtime = JobRuntime(SAFE_DEFAULT_FLAGS, audit.append)
    called = 0

    def operation():
        nonlocal called
        called += 1

    receipt = runtime.execute(JOB_REGISTRY.get("external-webhook-delivery"), idempotency_key="evt-1", operation=operation)
    assert receipt.state is JobState.DISABLED
    assert called == 0
    assert runtime.metrics[(receipt.job_name, JobState.DISABLED)] == 1
    assert audit[0]["reason"] == "feature_flag_disabled"


def test_duplicate_submission_runs_once_and_does_not_audit_raw_key():
    audit = []
    runtime = JobRuntime(FeatureFlags(), audit.append)
    calls = 0

    def operation():
        nonlocal calls
        calls += 1
        return {"finding_count": 3}

    job = JOB_REGISTRY.get("threat-model-analysis")
    first = runtime.execute(job, idempotency_key="customer-secret-key", operation=operation, correlation_id="corr-1")
    second = runtime.execute(job, idempotency_key="customer-secret-key", operation=operation, correlation_id="corr-2")
    assert first is second
    assert calls == 1
    assert runtime.metrics[(job.name, "duplicate")] == 1
    assert "customer-secret-key" not in str(audit)
    assert audit[-1]["reason"] == "duplicate_suppressed"


def test_failure_is_counted_and_audited_without_caching():
    audit = []
    runtime = JobRuntime(FeatureFlags(), audit.append)

    with pytest.raises(RuntimeError, match="offline"):
        runtime.execute(JOB_REGISTRY.get("threat-model-analysis"), idempotency_key="run-1", operation=lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    assert runtime.metrics[("threat-model-analysis", JobState.FAILED)] == 1
    assert audit[-1]["state"] is JobState.FAILED
