"""Deterministic job guardrails: correlation, metrics, audit, and deduplication."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from threading import Lock
from typing import Any

from app.core.feature_flags import FeatureFlags
from app.core.job_registry import JobDefinition, JobState

logger = logging.getLogger("clearglass.artemis.jobs")


@dataclass(frozen=True, slots=True)
class JobReceipt:
    job_name: str
    state: JobState
    correlation_id: str
    idempotency_key_hash: str
    duration_ms: float
    result: Any = None


class JobRuntime:
    """Process-local control suitable for deterministic handlers and unit tests.

    Production multi-replica handlers must provide a transactional IdempotencyStore;
    the default in-memory store deliberately makes no distributed guarantee.
    """

    def __init__(self, flags: FeatureFlags, audit_sink: Callable[[Mapping[str, Any]], None]) -> None:
        self.flags = flags
        self.audit_sink = audit_sink
        self.metrics: Counter[tuple[str, str]] = Counter()
        self._receipts: dict[tuple[str, str], JobReceipt] = {}
        self._lock = Lock()

    def execute(
        self,
        job: JobDefinition,
        *,
        idempotency_key: str,
        operation: Callable[[], Any],
        correlation_id: str | None = None,
    ) -> JobReceipt:
        correlation_id = correlation_id or f"job_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(idempotency_key.encode()).hexdigest()
        cache_key = (job.name, key_hash)
        if job.idempotency_required and not idempotency_key.strip():
            raise ValueError("idempotency_key is required")
        with self._lock:
            duplicate = self._receipts.get(cache_key)
        if duplicate is not None:
            self.metrics[(job.name, "duplicate")] += 1
            self._audit(job, JobState.SUCCEEDED, correlation_id, key_hash, "duplicate_suppressed")
            return duplicate
        if job.feature_flag is not None and not self.flags.enabled(job.feature_flag):
            receipt = JobReceipt(job.name, JobState.DISABLED, correlation_id, key_hash, 0.0)
            self.metrics[(job.name, JobState.DISABLED)] += 1
            self._audit(job, JobState.DISABLED, correlation_id, key_hash, "feature_flag_disabled")
            return receipt

        started = time.perf_counter()
        try:
            result = operation()
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            self.metrics[(job.name, JobState.FAILED)] += 1
            self._audit(job, JobState.FAILED, correlation_id, key_hash, "operation_failed")
            logger.exception(json.dumps({"event": "job_failed", "job": job.name, "correlation_id": correlation_id}))
            raise
        duration_ms = (time.perf_counter() - started) * 1000
        receipt = JobReceipt(job.name, JobState.SUCCEEDED, correlation_id, key_hash, duration_ms, result)
        with self._lock:
            self._receipts[cache_key] = receipt
        self.metrics[(job.name, JobState.SUCCEEDED)] += 1
        self._audit(job, JobState.SUCCEEDED, correlation_id, key_hash, "operation_completed")
        logger.info(json.dumps({"event": "job_completed", "job": job.name, "correlation_id": correlation_id, "duration_ms": round(duration_ms, 3)}))
        return receipt

    def _audit(self, job: JobDefinition, state: JobState, correlation_id: str, key_hash: str, reason: str) -> None:
        if job.audit_required:
            self.audit_sink({"event": "job_state_changed", "job": job.name, "owner": job.owner, "state": state, "reason": reason, "correlation_id": correlation_id, "idempotency_key_hash": key_hash})
