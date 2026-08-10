"""Thread-safe duplicate-submission guard for bounded local/runtime use."""
from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from operations.observability import JobTelemetry


class SubmissionState(StrEnum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Submission:
    scope: str
    key: str
    payload_digest: str
    state: SubmissionState
    expires_at: datetime
    result: Any = None


class IdempotencyConflict(ValueError):
    """A key was reused with a different request payload."""


class IdempotencyStore:
    def __init__(self, retention: timedelta, telemetry: JobTelemetry | None = None) -> None:
        if retention <= timedelta() or retention > timedelta(days=90):
            raise ValueError("retention must be between zero and 90 days")
        self._retention = retention
        self._telemetry = telemetry
        self._records: dict[tuple[str, str], Submission] = {}
        self._lock = threading.Lock()

    @staticmethod
    def digest(payload: Any) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def begin(self, scope: str, key: str, payload: Any, *, now: datetime | None = None) -> tuple[Submission, bool]:
        if not scope.strip() or len(key) < 8 or len(key) > 128:
            raise ValueError("scope is required and key must contain 8-128 characters")
        clock = now or datetime.now(timezone.utc)
        if clock.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        digest = self.digest(payload)
        record_key = (scope, key)
        with self._lock:
            self._records = {item: record for item, record in self._records.items() if record.expires_at > clock}
            existing = self._records.get(record_key)
            if existing:
                if existing.payload_digest != digest:
                    if self._telemetry:
                        self._telemetry.emit(scope, "idempotency-conflict", idempotency_key_hash=self.digest(key)[:16])
                    raise IdempotencyConflict("idempotency key was reused with a different payload")
                if self._telemetry:
                    self._telemetry.emit(scope, "duplicate", idempotency_key_hash=self.digest(key)[:16])
                return existing, True
            submission = Submission(scope, key, digest, SubmissionState.PROCESSING, clock + self._retention)
            self._records[record_key] = submission
            if self._telemetry:
                self._telemetry.emit(scope, "accepted", idempotency_key_hash=self.digest(key)[:16])
            return submission, False

    def complete(self, scope: str, key: str, result: Any) -> Submission:
        return self._transition(scope, key, SubmissionState.COMPLETED, result)

    def fail(self, scope: str, key: str) -> Submission:
        return self._transition(scope, key, SubmissionState.FAILED, None)

    def _transition(self, scope: str, key: str, state: SubmissionState, result: Any) -> Submission:
        with self._lock:
            try:
                current = self._records[(scope, key)]
            except KeyError as exc:
                raise LookupError("submission has not begun") from exc
            updated = Submission(scope, key, current.payload_digest, state, current.expires_at, result)
            self._records[(scope, key)] = updated
            return updated
