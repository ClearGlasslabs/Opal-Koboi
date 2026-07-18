from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import Base
from app.models.domain import ApprovalStatus
from app.schemas.domain import ProductCreate, ProductUpdate
from app.services.control_plane import create_product, decide_approval, request_product_update


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        api_key="x" * 32,
        database_url="sqlite+pysqlite:///:memory:",
        high_risk_price_delta_percent=20,
        high_risk_inventory_delta=100,
    )


def test_low_risk_update_applies_immediately(db: Session, settings: Settings) -> None:
    product = create_product(
        db,
        ProductCreate(
            actor="operator",
            request_id="request-0001",
            name="Sensor",
            description="",
            price=Decimal("100.00"),
            inventory_count=10,
        ),
    )
    result, updated, approval, risk = request_product_update(
        db,
        product.id,
        ProductUpdate(
            actor="operator",
            request_id="request-0002",
            expected_version=1,
            price=Decimal("105.00"),
        ),
        settings,
    )
    assert result == "applied"
    assert approval is None
    assert updated is not None
    assert updated.price == Decimal("105.00")
    assert updated.version == 2
    assert risk < 50


def test_high_risk_update_requires_independent_approval(db: Session, settings: Settings) -> None:
    product = create_product(
        db,
        ProductCreate(
            actor="operator",
            request_id="request-1001",
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
            request_id="request-1002",
            expected_version=1,
            price=Decimal("50.00"),
        ),
        settings,
    )
    assert result == "pending_approval"
    assert approval is not None
    assert risk >= 50

    with pytest.raises(HTTPException) as exc:
        decide_approval(db, approval.id, actor="operator", reason="self approve", approve=True)
    assert exc.value.status_code == 403

    decided = decide_approval(db, approval.id, actor="reviewer", reason="verified", approve=True)
    assert decided.status is ApprovalStatus.approved
    assert product.price == Decimal("50.00")
    assert product.version == 2
