"""Typed, fail-closed inventory of executable Artemis jobs.

The registry is configuration, not a scheduler.  It intentionally cannot contact a
provider or execute a job; runtimes must resolve an enabled definition first.
"""
from __future__ import annotations

from datetime import timedelta
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class JobLifecycle(StrEnum):
    LOADING = "loading"
    RETRYING = "retrying"
    DELAYED = "delayed"
    FAILED = "failed"
    DEAD_LETTERED = "dead-lettered"
    DISABLED = "disabled"
    MANUAL_REVIEW_REQUIRED = "manual-review-required"
    READY = "ready"
    RUNNING = "running"
    SUCCEEDED = "succeeded"


class TriggerType(StrEnum):
    API = "api"
    EVENT = "event"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class RetryPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    maximum_attempts: int = Field(ge=1, le=10)
    initial_backoff_seconds: int = Field(ge=1, le=3600)
    maximum_backoff_seconds: int = Field(ge=1, le=86400)

    @model_validator(mode="after")
    def valid_backoff(self) -> "RetryPolicy":
        if self.maximum_backoff_seconds < self.initial_backoff_seconds:
            raise ValueError("maximum backoff must not be less than initial backoff")
        return self


class JobDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    name: str = Field(pattern=r"^[a-z][a-z0-9_.-]{2,80}$")
    purpose: str = Field(min_length=10)
    owner: str = Field(min_length=3)
    trigger: TriggerType
    lifecycle: JobLifecycle = JobLifecycle.DISABLED
    feature_flag: str = Field(pattern=r"^[A-Z][A-Z0-9_]{2,80}$")
    timeout_seconds: int = Field(ge=1, le=3600)
    retry: RetryPolicy
    idempotency_required: bool
    idempotency_retention: timedelta | None = None
    data_retention: timedelta = Field(gt=timedelta())
    audit_required: bool = True
    rollback: str = Field(min_length=10)

    @model_validator(mode="after")
    def side_effect_controls_are_complete(self) -> "JobDefinition":
        if self.idempotency_required and self.idempotency_retention is None:
            raise ValueError("idempotent jobs require an idempotency retention period")
        return self


class JobRegistry:
    def __init__(self, definitions: tuple[JobDefinition, ...]) -> None:
        by_name = {definition.name: definition for definition in definitions}
        if len(by_name) != len(definitions):
            raise ValueError("job names must be unique")
        self._definitions = by_name

    def list(self) -> tuple[JobDefinition, ...]:
        return tuple(self._definitions[name] for name in sorted(self._definitions))

    def resolve(self, name: str, flags: dict[str, bool] | None = None) -> JobDefinition:
        """Resolve only runnable work; absent flags always fail closed."""
        try:
            definition = self._definitions[name]
        except KeyError as exc:
            raise LookupError("unregistered job") from exc
        if definition.lifecycle != JobLifecycle.READY:
            raise PermissionError(f"job is {definition.lifecycle.value}")
        if not (flags or {}).get(definition.feature_flag, False):
            raise PermissionError("job feature flag is disabled")
        return definition


JOB_REGISTRY = JobRegistry(
    (
        JobDefinition(
            name="platform.threat-analysis",
            purpose="Run deterministic, provider-free threat model analysis.",
            owner="platform-security",
            trigger=TriggerType.API,
            lifecycle=JobLifecycle.READY,
            feature_flag="ARTEMIS_THREAT_ANALYSIS_ENABLED",
            timeout_seconds=60,
            retry=RetryPolicy(maximum_attempts=2, initial_backoff_seconds=2, maximum_backoff_seconds=10),
            idempotency_required=True,
            idempotency_retention=timedelta(days=7),
            data_retention=timedelta(days=365),
            rollback="Disable ARTEMIS_THREAT_ANALYSIS_ENABLED and revert the registry entry.",
        ),
        JobDefinition(
            name="external.ai-enrichment",
            purpose="Reserved AI enrichment integration requiring explicit owner approval.",
            owner="ai-governance",
            trigger=TriggerType.EVENT,
            lifecycle=JobLifecycle.DISABLED,
            feature_flag="ARTEMIS_AI_ENABLED",
            timeout_seconds=30,
            retry=RetryPolicy(maximum_attempts=1, initial_backoff_seconds=1, maximum_backoff_seconds=1),
            idempotency_required=True,
            idempotency_retention=timedelta(days=7),
            data_retention=timedelta(days=30),
            rollback="Keep ARTEMIS_AI_ENABLED false and revert the registry entry.",
        ),
        JobDefinition(
            name="external.customer-notification",
            purpose="Reserved customer notification integration; no delivery is implemented.",
            owner="customer-operations",
            trigger=TriggerType.EVENT,
            lifecycle=JobLifecycle.DISABLED,
            feature_flag="ARTEMIS_CUSTOMER_MESSAGING_ENABLED",
            timeout_seconds=30,
            retry=RetryPolicy(maximum_attempts=1, initial_backoff_seconds=1, maximum_backoff_seconds=1),
            idempotency_required=True,
            idempotency_retention=timedelta(days=30),
            data_retention=timedelta(days=30),
            rollback="Keep ARTEMIS_CUSTOMER_MESSAGING_ENABLED false and revert the registry entry.",
        ),
    )
)
