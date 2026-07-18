from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.dependencies import Authorized, DbSession
from app.crud.event import list_events
from app.schemas.event import EventRead

router = APIRouter(prefix="/events", tags=["audit"])


@router.get("", response_model=list[EventRead])
def read_events(_: Authorized, db: DbSession, limit: int = Query(default=100, ge=1, le=1000)):
    return list_events(db, limit=limit)
