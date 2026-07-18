from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import Base
from app.crud.inventory import get_inventory_movement_by_request_id
from app.models.domain import Product as DomainProduct
from app.models.event import Event
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.approval_service import decide_approval
from app.services.product_service import create_product, request_product_update


def make_settings() -> Settings:
    return Settings(
        api_key="x" * 32,
        database_url="sqlite+pysqlite:///:memory:",
        high_risk_price_delta_percent=20,
        high_risk_inventory_delta=100,
    )


def test_compatibility_export_points_to_modular_product_model() -> None:
    assert DomainProduct is Product


def test_applied_inventory_change_creates_movement_and_hash_chain() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        product = create_product(
            db,
            ProductCreate(
                actor="operator",
                request_id="request-mod-0001",
                name="Sensor",
                description="",
                price=Decimal("100.00"),
                inventory_count=10,
            ),
        )
        result, updated, approval, _ = request_product_update(
            db,
            product.id,
            ProductUpdate(
                actor="operator",
                request_id="request-mod-0002",
                expected_version=1,
                inventory_count=15,
            ),
            make_settings(),
        )

        assert result == "applied"
        assert approval is None
        assert updated is product
        movement = get_inventory_movement_by_request_id(db, "request-mod-0002")
        assert movement is not None
        assert movement.quantity_delta == 5
        assert movement.resulting_inventory == 15

        events = list(db.scalars(select(Event).order_by(Event.created_at.asc())))
        assert len(events) == 2
        assert events[0].previous_hash == "0" * 64
        assert events[1].previous_hash == events[0].event_hash


def test_high_risk_inventory_change_records_movement_only_after_approval() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        product = create_product(
            db,
            ProductCreate(
                actor="operator",
                request_id="request-mod-1001",
                name="Sensor",
                description="",
                price=Decimal("100.00"),
                inventory_count=10,
            ),
        )
        result, _, approval, risk = request_product_update(
            db,
            product.id,
            ProductUpdate(
                actor="operator",
                request_id="request-mod-1002",
                expected_version=1,
                inventory_count=500,
            ),
            make_settings(),
        )

        assert result == "pending_approval"
        assert approval is not None
        assert risk >= 50
        assert get_inventory_movement_by_request_id(db, "request-mod-1002") is None

        decide_approval(db, approval.id, actor="reviewer", reason="verified", approve=True)
        movement = get_inventory_movement_by_request_id(db, "request-mod-1002")
        assert movement is not None
        assert movement.quantity_delta == 490
        assert movement.resulting_inventory == 500
