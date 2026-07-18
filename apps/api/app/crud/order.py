from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order


def get_order(db: Session, order_id: str) -> Order | None:
    return db.get(Order, order_id)


def list_orders(db: Session, *, limit: int = 100) -> list[Order]:
    return list(db.scalars(select(Order).order_by(Order.created_at.desc()).limit(limit)))


def insert_draft_order(
    db: Session,
    *,
    external_reference: str | None,
    currency: str,
    total_amount: Decimal,
) -> Order:
    order = Order(
        external_reference=external_reference,
        currency=currency.upper(),
        total_amount=total_amount,
    )
    db.add(order)
    db.flush()
    return order
