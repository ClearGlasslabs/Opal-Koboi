from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from app.crud.event import get_latest_event, insert_event
from app.models.event import Event


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def append_event(
    db: Session,
    *,
    request_id: str,
    actor: str,
    action: str,
    target: str,
    payload: dict[str, Any] | None,
    result: str,
    risk_score: int,
) -> Event:
    """Append one tamper-evident event inside the caller's transaction."""
    previous = get_latest_event(db)
    previous_hash = previous.event_hash if previous else "0" * 64
    material = canonical_json(
        {
            "request_id": request_id,
            "actor": actor,
            "action": action,
            "target": target,
            "payload": payload,
            "result": result,
            "risk_score": risk_score,
            "previous_hash": previous_hash,
        }
    )
    event_hash = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return insert_event(
        db,
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
