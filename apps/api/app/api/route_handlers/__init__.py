from fastapi import APIRouter

from app.api.route_handlers.approvals import router as approvals_router
from app.api.route_handlers.events import router as events_router
from app.api.route_handlers.health import router as health_router
from app.api.route_handlers.inventory import router as inventory_router
from app.api.route_handlers.products import router as products_router

router = APIRouter()
router.include_router(health_router)
router.include_router(products_router)
router.include_router(approvals_router)
router.include_router(events_router)
router.include_router(inventory_router)

__all__ = ["router"]
