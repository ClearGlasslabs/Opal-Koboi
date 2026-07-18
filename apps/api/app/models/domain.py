"""Backward-compatible model exports.

New code should import domain models from their dedicated modules. This module is
retained so existing callers and migrations continue to work without change.
"""

from app.models.approval import Approval, ApprovalStatus
from app.models.event import Event
from app.models.inventory import InventoryMovement
from app.models.order import Order, OrderStatus
from app.models.product import Product

__all__ = [
    "Approval",
    "ApprovalStatus",
    "Event",
    "InventoryMovement",
    "Order",
    "OrderStatus",
    "Product",
]
