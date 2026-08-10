"""Central typed registry for governed ClearGlassInc Artemis jobs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from app.core.feature_flags import Capability


class JobState(StrEnum):
    LOADING = "loading"
    RETRYING = "retrying"
    DELAYED = "delayed"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"
    DISABLED = "disabled"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    SUCCEEDED = "succeeded"


class Trigger(StrEnum):
    HTTP = "http"
    SCHEDULE = "schedule"
    EVENT = "event"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int
    backoff_seconds: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.max_attempts < 1 or len(self.backoff_seconds) != self.max_attempts - 1:
            raise ValueError("retry backoff must describe every retry")


@dataclass(frozen=True, slots=True)
class JobDefinition:
    name: str
    purpose: str
    owner: str
    trigger: Trigger
    lifecycle: frozenset[JobState]
    feature_flag: Capability | None
    timeout_seconds: int
    retry: RetryPolicy
    idempotency_required: bool
    retention_days: int
    audit_required: bool
    rollback: str

    def __post_init__(self) -> None:
        if not self.name or not self.owner or not self.purpose or not self.rollback:
            raise ValueError("job identity, ownership, purpose, and rollback are required")
        if self.timeout_seconds < 1 or self.retention_days < 1:
            raise ValueError("timeout and retention must be positive")
        if JobState.FAILED not in self.lifecycle or JobState.SUCCEEDED not in self.lifecycle:
            raise ValueError("jobs must define success and failure behavior")


class JobRegistry:
    def __init__(self, jobs: tuple[JobDefinition, ...]) -> None:
        indexed = {job.name: job for job in jobs}
        if len(indexed) != len(jobs):
            raise ValueError("job names must be unique")
        self._jobs: Mapping[str, JobDefinition] = MappingProxyType(indexed)

    def get(self, name: str) -> JobDefinition:
        try:
            return self._jobs[name]
        except KeyError as exc:
            raise KeyError(f"unregistered job: {name}") from exc

    def snapshot(self) -> Mapping[str, JobDefinition]:
        return self._jobs


STANDARD_LIFECYCLE = frozenset(JobState)
JOB_REGISTRY = JobRegistry(
    (
        JobDefinition(
            name="threat-model-analysis",
            purpose="Run deterministic defensive architecture rules and persist evidence.",
            owner="Artemis Security Architecture",
            trigger=Trigger.HTTP,
            lifecycle=STANDARD_LIFECYCLE,
            feature_flag=None,
            timeout_seconds=30,
            retry=RetryPolicy(2, (2,)),
            idempotency_required=True,
            retention_days=2555,
            audit_required=True,
            rollback="Disable the analysis route and revert the registry/runtime commit; retained evidence is append-only.",
        ),
        JobDefinition(
            name="external-webhook-delivery",
            purpose="Reserved outbound webhook delivery capability; no provider is connected.",
            owner="Artemis Platform Operations",
            trigger=Trigger.EVENT,
            lifecycle=STANDARD_LIFECYCLE,
            feature_flag=Capability.EXTERNAL_WEBHOOKS,
            timeout_seconds=10,
            retry=RetryPolicy(1, ()),
            idempotency_required=True,
            retention_days=90,
            audit_required=True,
            rollback="Set external_webhooks false (the default) and remove any separately approved adapter.",
        ),
    )
)
