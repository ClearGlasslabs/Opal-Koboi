from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from operations.idempotency import IdempotencyConflict, IdempotencyStore, SubmissionState
from operations.job_registry import JOB_REGISTRY, JobDefinition, JobLifecycle
from operations.observability import JobTelemetry, bind_correlation_id, reset_correlation_id


def test_registry_is_complete_unique_and_fail_closed() -> None:
    definitions = JOB_REGISTRY.list()
    assert len(definitions) == len({job.name for job in definitions})
    assert {job.lifecycle for job in definitions} >= {JobLifecycle.READY, JobLifecycle.DISABLED}
    with pytest.raises(PermissionError, match="feature flag"):
        JOB_REGISTRY.resolve("platform.threat-analysis")
    with pytest.raises(PermissionError, match="disabled"):
        JOB_REGISTRY.resolve("external.ai-enrichment", {"ARTEMIS_AI_ENABLED": True})
    assert JOB_REGISTRY.resolve(
        "platform.threat-analysis", {"ARTEMIS_THREAT_ANALYSIS_ENABLED": True}
    ).owner == "platform-security"


def test_registry_rejects_missing_idempotency_retention() -> None:
    payload = JOB_REGISTRY.list()[0].model_dump()
    payload["idempotency_retention"] = None
    with pytest.raises(ValidationError, match="retention"):
        JobDefinition.model_validate(payload)


def test_job_telemetry_correlates_redacts_metrics_and_failure_audit() -> None:
    telemetry = JobTelemetry()
    token = bind_correlation_id("corr-test-12345")
    try:
        with pytest.raises(RuntimeError):
            with telemetry.track("platform.test"):
                raise RuntimeError("controlled failure")
        telemetry.emit("platform.test", "manual-review-required", token="do-not-log")
    finally:
        reset_correlation_id(token)

    events = telemetry.audit_events()
    assert [event["state"] for event in events] == ["running", "failed", "manual-review-required"]
    assert all(event["correlation_id"] == "corr-test-12345" for event in events)
    assert events[-1]["token"] == "[REDACTED]"
    assert telemetry.metrics()['artemis_job_total{job="platform.test",state="failed"}'] == 1


def test_idempotency_replays_result_rejects_payload_conflict_and_expires() -> None:
    telemetry = JobTelemetry()
    token = bind_correlation_id("corr-idem-12345")
    try:
        store = IdempotencyStore(timedelta(hours=1), telemetry)
        now = datetime(2026, 8, 10, tzinfo=timezone.utc)
        first, duplicate = store.begin("contact.submit", "request-123", {"message": "hello"}, now=now)
        assert not duplicate and first.state == SubmissionState.PROCESSING
        completed = store.complete("contact.submit", "request-123", {"accepted": True})
        replay, duplicate = store.begin("contact.submit", "request-123", {"message": "hello"}, now=now)
        assert duplicate and replay == completed
        with pytest.raises(IdempotencyConflict):
            store.begin("contact.submit", "request-123", {"message": "changed"}, now=now)
        replacement, duplicate = store.begin(
            "contact.submit", "request-123", {"message": "changed"}, now=now + timedelta(hours=2)
        )
        assert not duplicate and replacement.state == SubmissionState.PROCESSING
    finally:
        reset_correlation_id(token)
