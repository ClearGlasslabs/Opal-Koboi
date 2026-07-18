"""Backward-compatible API router export.

Route implementations are separated by domain under ``route_handlers`` while
this module preserves the original ``app.api.routes:router`` import path.
"""

from app.api.route_handlers import router

__all__ = ["router"]
