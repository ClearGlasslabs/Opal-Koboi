from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_product(db: Session, product_id: str) -> Product | None:
    return db.get(Product, product_id)


def list_products(db: Session, *, limit: int = 100) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.created_at.desc()).limit(limit)))


def insert_product(
    db: Session,
    *,
    name: str,
    description: str,
    price: Decimal,
    inventory_count: int,
) -> Product:
    product = Product(
        name=name,
        description=description,
        price=price,
        inventory_count=inventory_count,
    )
    db.add(product)
    db.flush()
    return product


def apply_product_update(product: Product, payload: dict[str, Any]) -> None:
    for key in ("name", "description", "price", "inventory_count"):
        if key in payload and payload[key] is not None:
            value = Decimal(payload[key]) if key == "price" else payload[key]
            setattr(product, key, value)
    product.version += 1
