"""Create control-plane products, approvals, and tamper-evident event ledger."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_control_plane"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

approval_status = sa.Enum("pending", "approved", "rejected", name="approval_status")


def upgrade() -> None:
    approval_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("inventory_count", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("inventory_count >= 0", name="ck_products_inventory_nonnegative"),
        sa.CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_name", "products", ["name"], unique=False)

    op.create_table(
        "approvals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("target_type", sa.String(length=128), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("status", approval_status, nullable=False),
        sa.Column("decided_by", sa.String(length=255)),
        sa.Column("decision_reason", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index("ix_approvals_request_id", "approvals", ["request_id"], unique=True)
    op.create_index("ix_approvals_target_id", "approvals", ["target_id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("target", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON()),
        sa.Column("result", sa.String(length=64), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("previous_hash", sa.String(length=64), nullable=False),
        sa.Column("event_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_hash"),
    )
    op.create_index("ix_events_request_id", "events", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_events_request_id", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_approvals_target_id", table_name="approvals")
    op.drop_index("ix_approvals_request_id", table_name="approvals")
    op.drop_table("approvals")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")
    approval_status.drop(op.get_bind(), checkfirst=True)
