from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select, text

from app.api.dependencies import AppSettings, Authorized, DbSession
from app.models.domain import Approval, Event, Product
from app.schemas.domain import (
    ApprovalDecision,
    ApprovalRead,
    EventRead,
    MutationResult,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.services.control_plane import (
    create_product,
    decide_approval,
    get_product_or_404,
    request_product_update,
)

router = APIRouter()


@router.get("/health", tags=["health"])
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/products", response_model=list[ProductRead], tags=["products"])
def list_products(_: Authorized, db: DbSession, limit: int = Query(default=100, ge=1, le=500)):
    return list(db.scalars(select(Product).order_by(Product.created_at.desc()).limit(limit)))


@router.get("/products/{product_id}", response_model=ProductRead, tags=["products"])
def read_product(product_id: str, _: Authorized, db: DbSession):
    return get_product_or_404(db, product_id)


@router.post("/products", response_model=ProductRead, status_code=201, tags=["products"])
def add_product(command: ProductCreate, _: Authorized, db: DbSession):
    return create_product(db, command)


@router.patch("/products/{product_id}", response_model=MutationResult, tags=["products"])
def edit_product(
    product_id: str,
    command: ProductUpdate,
    _: Authorized,
    db: DbSession,
    settings: AppSettings,
):
    result, product, approval, risk = request_product_update(db, product_id, command, settings)
    return MutationResult(
        status=result,
        product=product,
        approval_id=approval.id if approval else None,
        risk_score=risk,
    )


@router.get("/approvals", response_model=list[ApprovalRead], tags=["approvals"])
def list_approvals(
    _: Authorized,
    db: DbSession,
    status_filter: str | None = Query(default=None, alias="status"),
):
    statement = select(Approval).order_by(Approval.created_at.desc())
    if status_filter:
        statement = statement.where(Approval.status == status_filter)
    return list(db.scalars(statement.limit(500)))


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalRead, tags=["approvals"])
def approve_change(
    approval_id: str, decision: ApprovalDecision, _: Authorized, db: DbSession
):
    return decide_approval(
        db, approval_id, actor=decision.actor, reason=decision.reason, approve=True
    )


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalRead, tags=["approvals"])
def reject_change(
    approval_id: str, decision: ApprovalDecision, _: Authorized, db: DbSession
):
    return decide_approval(
        db, approval_id, actor=decision.actor, reason=decision.reason, approve=False
    )


@router.get("/events", response_model=list[EventRead], tags=["audit"])
def list_events(_: Authorized, db: DbSession, limit: int = Query(default=100, ge=1, le=1000)):
    return list(db.scalars(select(Event).order_by(Event.created_at.desc()).limit(limit)))
