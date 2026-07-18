from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryMovement


def get_inventory_movement_by_request_id(
    db: Session, request_id: str
) -> InventoryMovement | None:
    return db.scalar(
        select(InventoryMovement).where(InventoryMovement.request_id == request_id).limit(1)
    )


def list_inventory_movements(
    db: Session, *, product_id: str | None = None, limit: int = 500
) -> list[InventoryMovement]:
    statement = select(InventoryMovement).order_by(InventoryMovement.created_at.desc())
    if product_id:
        statement = statement.where(InventoryMovement.product_id == product_id)
    return list(db.scalars(statement.limit(limit)))


def insert_inventory_movement(
    db: Session,
    *,
    request_id: str,
    product_id: str,
    actor: str,
    reason: str,
    quantity_delta: int,
    resulting_inventory: int,
) -> InventoryMovement:
    movement = InventoryMovement(
        request_id=request_id,
        product_id=product_id,
        actor=actor,
        reason=reason,
        quantity_delta=quantity_delta,
        resulting_inventory=resulting_inventory,
    )
    db.add(movement)
    db.flush()
    return movement
