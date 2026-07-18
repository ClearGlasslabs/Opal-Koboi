from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event


def get_event_by_request_id(db: Session, request_id: str) -> Event | None:
    return db.scalar(select(Event).where(Event.request_id == request_id).limit(1))


def get_latest_event(db: Session) -> Event | None:
    return db.scalar(select(Event).order_by(Event.created_at.desc(), Event.id.desc()).limit(1))


def list_events(db: Session, *, limit: int = 100) -> list[Event]:
    return list(db.scalars(select(Event).order_by(Event.created_at.desc()).limit(limit)))


def insert_event(
    db: Session,
    *,
    request_id: str,
    actor: str,
    action: str,
    target: str,
    payload: dict[str, Any] | None,
    result: str,
    risk_score: int,
    previous_hash: str,
    event_hash: str,
) -> Event:
    event = Event(
        request_id=request_id,
        actor=actor,
        action=action,
        target=target,
        payload=payload,
        result=result,
        risk_score=risk_score,
        previous_hash=previous_hash,
        event_hash=event_hash,
    )
    db.add(event)
    db.flush()
    return event
