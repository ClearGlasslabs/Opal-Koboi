from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.dependencies import Authorized, DbSession
from app.crud.inventory import list_inventory_movements
from app.schemas.inventory import InventoryMovementRead

router = APIRouter(prefix="/inventory-movements", tags=["inventory", "audit"])


@router.get("", response_model=list[InventoryMovementRead])
def read_inventory_movements(
    _: Authorized,
    db: DbSession,
    product_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return list_inventory_movements(db, product_id=product_id, limit=limit)
