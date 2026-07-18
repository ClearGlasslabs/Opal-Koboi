from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.crud.approval import insert_approval
from app.crud.event import get_event_by_request_id
from app.crud.inventory import insert_inventory_movement
from app.crud.product import apply_product_update, get_product, insert_product
from app.models.approval import Approval
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.audit_service import append_event


def get_product_or_404(db: Session, product_id: str) -> Product:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def ensure_request_is_new(db: Session, request_id: str) -> None:
    if get_event_by_request_id(db, request_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="request_id already processed")


def record_inventory_change(
    db: Session,
    *,
    request_id: str,
    product: Product,
    actor: str,
    reason: str,
    previous_inventory: int,
) -> None:
    delta = product.inventory_count - previous_inventory
    if delta == 0:
        return
    insert_inventory_movement(
        db,
        request_id=request_id,
        product_id=product.id,
        actor=actor,
        reason=reason,
        quantity_delta=delta,
        resulting_inventory=product.inventory_count,
    )


def create_product(db: Session, command: ProductCreate) -> Product:
    ensure_request_is_new(db, command.request_id)
    product = insert_product(
        db,
        name=command.name,
        description=command.description,
        price=command.price,
        inventory_count=command.inventory_count,
    )
    if product.inventory_count:
        insert_inventory_movement(
            db,
            request_id=command.request_id,
            product_id=product.id,
            actor=command.actor,
            reason="product.create initial inventory",
            quantity_delta=product.inventory_count,
            resulting_inventory=product.inventory_count,
        )
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
    """Compatibility wrapper around the product persistence mutation."""
    apply_product_update(product, payload)


def request_product_update(
    db: Session, product_id: str, command: ProductUpdate, settings: Settings
) -> tuple[str, Product | None, Approval | None, int]:
    product = get_product_or_404(db, product_id)
    if product.version != command.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Version conflict", "current_version": product.version},
        )
    ensure_request_is_new(db, command.request_id)
    payload = command.model_dump(
        mode="json", exclude={"actor", "request_id", "expected_version"}, exclude_none=True
    )
    risk = calculate_update_risk(product, command, settings)
    if risk >= 50:
        approval = insert_approval(
            db,
            request_id=command.request_id,
            actor=command.actor,
            action="product.update",
            target_type="product",
            target_id=product.id,
            payload={**payload, "expected_version": command.expected_version},
            risk_score=risk,
        )
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

    previous_inventory = product.inventory_count
    apply_product_update(product, payload)
    record_inventory_change(
        db,
        request_id=command.request_id,
        product=product,
        actor=command.actor,
        reason="product.update applied",
        previous_inventory=previous_inventory,
    )
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
