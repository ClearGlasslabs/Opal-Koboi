from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    request_id: str
    product_id: str
    actor: str
    reason: str
    quantity_delta: int
    resulting_inventory: int
    created_at: datetime
