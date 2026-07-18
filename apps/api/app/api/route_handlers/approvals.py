from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.dependencies import Authorized, DbSession
from app.crud.approval import list_approvals
from app.schemas.approval import ApprovalDecision, ApprovalRead
from app.services.approval_service import decide_approval

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalRead])
def read_approvals(
    _: Authorized,
    db: DbSession,
    status_filter: str | None = Query(default=None, alias="status"),
):
    return list_approvals(db, status_filter=status_filter, limit=500)


@router.post("/{approval_id}/approve", response_model=ApprovalRead)
def approve_change(
    approval_id: str, decision: ApprovalDecision, _: Authorized, db: DbSession
):
    return decide_approval(
        db, approval_id, actor=decision.actor, reason=decision.reason, approve=True
    )


@router.post("/{approval_id}/reject", response_model=ApprovalRead)
def reject_change(
    approval_id: str, decision: ApprovalDecision, _: Authorized, db: DbSession
):
    return decide_approval(
        db, approval_id, actor=decision.actor, reason=decision.reason, approve=False
    )
