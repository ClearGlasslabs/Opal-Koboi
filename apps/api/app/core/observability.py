from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.responses import JSONResponse

LOGGER_NAME = "clearglass.artemis.api"
logger = logging.getLogger(LOGGER_NAME)
_request_windows: dict[str, deque[float]] = defaultdict(deque)


def configure_logging() -> None:
    """Configure structured-enough logging for container and Apollo runtimes."""

    if logging.getLogger().handlers:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


async def request_telemetry_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach request correlation, latency metrics, and safe audit logs.

    The middleware avoids body logging and secret capture. It provides a low-cost
    observability spine that works before a full OpenTelemetry collector is wired
    into Apollo/Foundry operations.
    """

    request_id = request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex}"
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "request_failed request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = f"{duration_ms:.2f}"
    logger.info(
        "request_completed request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def apply_security_headers(response: Response) -> None:
    """Apply hardened browser/API headers without changing route behavior."""

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault(
        "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
    response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")


def enforce_rate_limit(request: Request, *, limit: int, window_seconds: int) -> Response | None:
    """Small single-process safety net; production edges must enforce distributed quotas."""
    identity = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    if not identity:
        identity = request.client.host if request.client else "unknown"
    key = f"{identity}:{request.url.path}"
    now = time.monotonic()
    window = _request_windows[key]
    while window and window[0] <= now - window_seconds:
        window.popleft()
    if len(window) >= limit:
        logger.warning("request_throttled path=%s", request.url.path)
        return JSONResponse(
            status_code=429,
            content={"detail": "Request quota exceeded"},
            headers={"Retry-After": str(window_seconds)},
        )
    window.append(now)
    return None
