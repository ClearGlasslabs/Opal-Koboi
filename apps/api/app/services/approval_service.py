from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.approval import get_approval
from app.crud.product import apply_product_update
from app.models.approval import Approval, ApprovalStatus
from app.services.audit_service import append_event
from app.services.product_service import get_product_or_404, record_inventory_change


def decide_approval(
    db: Session,
    approval_id: str,
    *,
    actor: str,
    reason: str,
    approve: bool,
) -> Approval:
    approval = get_approval(db, approval_id)
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    if approval.status is not ApprovalStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Approval already decided")
    if actor == approval.actor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Four-eyes control: requester cannot approve their own change",
        )

    approval.decided_by = actor
    approval.decision_reason = reason
    approval.decided_at = datetime.now(UTC)
    if approve:
        product = get_product_or_404(db, approval.target_id)
        expected_version = int(approval.payload["expected_version"])
        if product.version != expected_version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Target changed after approval request", "current_version": product.version},
            )
        previous_inventory = product.inventory_count
        apply_product_update(product, approval.payload)
        record_inventory_change(
            db,
            request_id=approval.request_id,
            product=product,
            actor=approval.actor,
            reason=f"approved by {actor}: {reason}",
            previous_inventory=previous_inventory,
        )
        approval.status = ApprovalStatus.approved
        result = "approved_and_applied"
    else:
        approval.status = ApprovalStatus.rejected
        result = "rejected"

    db.flush()
    append_event(
        db,
        request_id=f"{approval.request_id}:{approval.status.value}",
        actor=actor,
        action=f"approval.{approval.status.value}",
        target=f"approval:{approval.id}",
        payload={"reason": reason, "original_request_id": approval.request_id},
        result=result,
        risk_score=approval.risk_score,
    )
    return approval
