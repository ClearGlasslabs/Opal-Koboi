from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.domain import Approval, ApprovalStatus, Event, Product
from app.schemas.domain import ProductCreate, ProductUpdate


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
    previous = db.scalar(select(Event).order_by(Event.created_at.desc(), Event.id.desc()).limit(1))
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
    event = Event(
        request_id=request_id,
        actor=actor,
        action=action,
        target=target,
        payload=payload,
        result=result,
        risk_score=risk_score,
        previous_hash=previous_hash,
        event_hash=hashlib.sha256(material.encode("utf-8")).hexdigest(),
    )
    db.add(event)
    db.flush()
    return event


def get_product_or_404(db: Session, product_id: str) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def create_product(db: Session, command: ProductCreate) -> Product:
    duplicate = db.scalar(select(Event).where(Event.request_id == command.request_id).limit(1))
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="request_id already processed")
    product = Product(
        name=command.name,
        description=command.description,
        price=command.price,
        inventory_count=command.inventory_count,
    )
    db.add(product)
    db.flush()
    append_event(
        db,
        request_id=command.request_id,
        actor=command.actor,
        action="product.create",
        target=f"product:{product.id}",
        payload=command.model_dump(mode="json", exclude={"actor", "request_id"}),
        result="applied",
        risk_score=10,
    )
    return product


def calculate_update_risk(product: Product, command: ProductUpdate, settings: Settings) -> int:
    score = 0
    if command.price is not None and product.price != command.price:
        old = Decimal(product.price)
        if old == 0:
            score += 70
        else:
            delta = abs((command.price - old) / old * Decimal("100"))
            score += 70 if delta >= settings.high_risk_price_delta_percent else 20
    if command.inventory_count is not None:
        delta_count = abs(command.inventory_count - product.inventory_count)
        score += 50 if delta_count >= settings.high_risk_inventory_delta else 10
    if command.name is not None or command.description is not None:
        score += 5
    return min(score, 100)


def apply_update(product: Product, payload: dict[str, Any]) -> None:
    for key in ("name", "description", "price", "inventory_count"):
        if key in payload and payload[key] is not None:
            value = Decimal(payload[key]) if key == "price" else payload[key]
            setattr(product, key, value)
    product.version += 1


def request_product_update(
    db: Session, product_id: str, command: ProductUpdate, settings: Settings
) -> tuple[str, Product | None, Approval | None, int]:
    product = get_product_or_404(db, product_id)
    if product.version != command.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Version conflict", "current_version": product.version},
        )
    if db.scalar(select(Event).where(Event.request_id == command.request_id).limit(1)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="request_id already processed")
    payload = command.model_dump(
        mode="json", exclude={"actor", "request_id", "expected_version"}, exclude_none=True
    )
    risk = calculate_update_risk(product, command, settings)
    if risk >= 50:
        approval = Approval(
            request_id=command.request_id,
            actor=command.actor,
            action="product.update",
            target_type="product",
            target_id=product.id,
            payload={**payload, "expected_version": command.expected_version},
            risk_score=risk,
        )
        db.add(approval)
        db.flush()
        append_event(
            db,
            request_id=command.request_id,
            actor=command.actor,
            action="product.update.requested",
            target=f"product:{product.id}",
            payload=payload,
            result="pending_approval",
            risk_score=risk,
        )
        return "pending_approval", None, approval, risk

    apply_update(product, payload)
    db.flush()
    append_event(
        db,
        request_id=command.request_id,
        actor=command.actor,
        action="product.update",
        target=f"product:{product.id}",
        payload=payload,
        result="applied",
        risk_score=risk,
    )
    return "applied", product, None, risk


def decide_approval(
    db: Session,
    approval_id: str,
    *,
    actor: str,
    reason: str,
    approve: bool,
) -> Approval:
    approval = db.get(Approval, approval_id)
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
        apply_update(product, approval.payload)
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
