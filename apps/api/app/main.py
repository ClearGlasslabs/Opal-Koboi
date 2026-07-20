from __future__ import annotations

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.observability import apply_security_headers, configure_logging, request_telemetry_middleware

configure_logging()
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type", "X-Control-Plane-Key"],
    )


@app.middleware("http")
async def telemetry_and_security_headers(request: Request, call_next):
    response: Response = await request_telemetry_middleware(request, call_next)
    apply_security_headers(response)
    return response


app.include_router(router, prefix="/api/v1")
