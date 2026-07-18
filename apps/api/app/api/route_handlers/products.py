from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.dependencies import AppSettings, Authorized, DbSession
from app.crud.product import list_products
from app.schemas.product import MutationResult, ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import create_product, get_product_or_404, request_product_update

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def read_products(_: Authorized, db: DbSession, limit: int = Query(default=100, ge=1, le=500)):
    return list_products(db, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def read_product(product_id: str, _: Authorized, db: DbSession):
    return get_product_or_404(db, product_id)


@router.post("", response_model=ProductRead, status_code=201)
def add_product(command: ProductCreate, _: Authorized, db: DbSession):
    return create_product(db, command)


@router.patch("/{product_id}", response_model=MutationResult)
def edit_product(
    product_id: str,
    command: ProductUpdate,
    _: Authorized,
    db: DbSession,
    settings: AppSettings,
):
    result, product, approval, risk = request_product_update(db, product_id, command, settings)
    return MutationResult(
        status=result,
        product=product,
        approval_id=approval.id if approval else None,
        risk_score=risk,
    )
