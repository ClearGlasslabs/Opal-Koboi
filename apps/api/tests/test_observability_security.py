from __future__ import annotations

from types import SimpleNamespace

import asyncio
from starlette.responses import Response

from app.core.observability import apply_security_headers, request_telemetry_middleware


def test_request_telemetry_adds_correlation_and_latency_headers():
    request = SimpleNamespace(
        headers={"x-request-id": "req-test-001"},
        method="GET",
        url=SimpleNamespace(path="/api/v1/health"),
    )

    async def call_next(_request):
        return Response(status_code=200)

    response = asyncio.run(request_telemetry_middleware(request, call_next))

    assert response.headers["X-Request-ID"] == "req-test-001"
    assert float(response.headers["X-Response-Time-ms"]) >= 0


def test_apply_security_headers_sets_hardened_defaults():
    response = Response(status_code=200)

    apply_security_headers(response)

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"
    assert response.headers["Cache-Control"] == "no-store"
