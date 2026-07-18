"""Add governed orders and append-only inventory movements."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_orders_inventory"
down_revision: Union[str, Sequence[str], None] = "0001_control_plane"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

order_status = sa.Enum(
    "draft",
    "pending_approval",
    "approved",
    "cancelled",
    name="order_status",
)


def upgrade() -> None:
    order_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("external_reference", sa.String(length=128), nullable=True),
        sa.Column("status", order_status, nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("total_amount >= 0", name="ck_orders_total_nonnegative"),
        sa.CheckConstraint("version >= 1", name="ck_orders_version_positive"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_reference"),
    )
    op.create_index(
        "ix_orders_external_reference", "orders", ["external_reference"], unique=True
    )

    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("quantity_delta", sa.Integer(), nullable=False),
        sa.Column("resulting_inventory", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "quantity_delta != 0", name="ck_inventory_movements_delta_nonzero"
        ),
        sa.CheckConstraint(
            "resulting_inventory >= 0", name="ck_inventory_movements_result_nonnegative"
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        "ix_inventory_movements_product_id",
        "inventory_movements",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        "ix_inventory_movements_request_id",
        "inventory_movements",
        ["request_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_movements_request_id", table_name="inventory_movements")
    op.drop_index("ix_inventory_movements_product_id", table_name="inventory_movements")
    op.drop_table("inventory_movements")
    op.drop_index("ix_orders_external_reference", table_name="orders")
    op.drop_table("orders")
    order_status.drop(op.get_bind(), checkfirst=True)
