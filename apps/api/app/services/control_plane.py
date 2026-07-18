"""Backward-compatible control-plane service exports.

The implementation is split into product, approval, and audit services. This
module remains as a stable import surface for existing callers and tests.
"""

from app.services.approval_service import decide_approval
from app.services.audit_service import append_event, canonical_json
from app.services.product_service import (
    apply_update,
    calculate_update_risk,
    create_product,
    get_product_or_404,
    request_product_update,
)

__all__ = [
    "append_event",
    "apply_update",
    "calculate_update_risk",
    "canonical_json",
    "create_product",
    "decide_approval",
    "get_product_or_404",
    "request_product_update",
]
