from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import Approval


def get_approval(db: Session, approval_id: str) -> Approval | None:
    return db.get(Approval, approval_id)


def list_approvals(
    db: Session,
    *,
    status_filter: str | None = None,
    limit: int = 500,
) -> list[Approval]:
    statement = select(Approval).order_by(Approval.created_at.desc())
    if status_filter:
        statement = statement.where(Approval.status == status_filter)
    return list(db.scalars(statement.limit(limit)))


def insert_approval(
    db: Session,
    *,
    request_id: str,
    actor: str,
    action: str,
    target_type: str,
    target_id: str,
    payload: dict[str, Any],
    risk_score: int,
) -> Approval:
    approval = Approval(
        request_id=request_id,
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        payload=payload,
        risk_score=risk_score,
    )
    db.add(approval)
    db.flush()
    return approval
