"""Dependency-free correlation, structured logging, metrics, and audit events."""
from __future__ import annotations

import json
import logging
import re
import threading
from collections import Counter
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from time import monotonic
from typing import Any
from uuid import uuid4

_CORRELATION_ID: ContextVar[str | None] = ContextVar("artemis_correlation_id", default=None)
_VALID_CORRELATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,127}$")
_SENSITIVE_KEYS = {"authorization", "cookie", "password", "secret", "token"}


def bind_correlation_id(value: str | None = None) -> Token[str | None]:
    correlation_id = value or f"corr-{uuid4().hex}"
    if not _VALID_CORRELATION_ID.fullmatch(correlation_id):
        raise ValueError("invalid correlation ID")
    return _CORRELATION_ID.set(correlation_id)


def current_correlation_id() -> str:
    value = _CORRELATION_ID.get()
    if value is None:
        raise RuntimeError("correlation ID has not been bound")
    return value


def reset_correlation_id(token: Token[str | None]) -> None:
    _CORRELATION_ID.reset(token)


def _redact(fields: dict[str, Any]) -> dict[str, Any]:
    return {key: "[REDACTED]" if key.lower() in _SENSITIVE_KEYS else value for key, value in fields.items()}


class JobTelemetry:
    """Small runtime-neutral adapter; exporters can consume snapshots and audit events."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("artemis.jobs")
        self._metrics: Counter[tuple[str, str]] = Counter()
        self._audit: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def emit(self, job: str, state: str, *, duration_seconds: float | None = None, **fields: Any) -> None:
        correlation_id = current_correlation_id()
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "job.lifecycle",
            "job": job,
            "state": state,
            "correlation_id": correlation_id,
            **_redact(fields),
        }
        if duration_seconds is not None:
            event["duration_seconds"] = round(duration_seconds, 6)
        with self._lock:
            self._metrics[(job, state)] += 1
            self._audit.append(event)
        self._logger.info(json.dumps(event, sort_keys=True, default=str))

    def track(self, job: str) -> "JobRun":
        return JobRun(self, job)

    def metrics(self) -> dict[str, int]:
        with self._lock:
            return {f'artemis_job_total{{job="{job}",state="{state}"}}': count for (job, state), count in self._metrics.items()}

    def audit_events(self) -> tuple[dict[str, Any], ...]:
        with self._lock:
            return tuple(dict(event) for event in self._audit)


class JobRun:
    def __init__(self, telemetry: JobTelemetry, job: str) -> None:
        self._telemetry = telemetry
        self._job = job
        self._started = 0.0

    def __enter__(self) -> "JobRun":
        self._started = monotonic()
        self._telemetry.emit(self._job, "running")
        return self

    def __exit__(self, exception_type: type[BaseException] | None, *_: Any) -> bool:
        state = "succeeded" if exception_type is None else "failed"
        self._telemetry.emit(self._job, state, duration_seconds=monotonic() - self._started)
        return False
