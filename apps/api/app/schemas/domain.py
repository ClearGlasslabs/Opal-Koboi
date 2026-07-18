"""Backward-compatible schema exports.

New code should import request and response schemas from their dedicated domain
modules. Existing imports remain valid through this compatibility surface.
"""

from app.schemas.approval import ApprovalDecision, ApprovalRead
from app.schemas.common import ActorContext
from app.schemas.event import EventCreate, EventRead
from app.schemas.inventory import InventoryMovementRead
from app.schemas.order import OrderCreate, OrderRead
from app.schemas.product import MutationResult, ProductCreate, ProductRead, ProductUpdate

__all__ = [
    "ActorContext",
    "ApprovalDecision",
    "ApprovalRead",
    "EventCreate",
    "EventRead",
    "InventoryMovementRead",
    "MutationResult",
    "OrderCreate",
    "OrderRead",
    "ProductCreate",
    "ProductRead",
    "ProductUpdate",
]
