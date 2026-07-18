"""Add deterministic autonomous threat modeling and evidence records."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_autonomous_threat_modeling"
down_revision: Union[str, Sequence[str], None] = "0002_orders_inventory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

threat_model_status = sa.Enum("draft", "analyzed", "archived", name="threat_model_status")
threat_analysis_run_status = sa.Enum("completed", "failed", name="threat_analysis_run_status")
threat_finding_status = sa.Enum(
    "open", "accepted", "mitigated", "false_positive", name="threat_finding_status"
)
threat_category = sa.Enum(
    "spoofing",
    "tampering",
    "repudiation",
    "information_disclosure",
    "denial_of_service",
    "elevation_of_privilege",
    "prompt_injection",
    "tool_abuse",
    "memory_poisoning",
    "agent_collusion",
    "sensor_spoofing",
    "actuator_hijacking",
    "supply_chain",
    name="threat_category",
)


def upgrade() -> None:
    bind = op.get_bind()
    threat_model_status.create(bind, checkfirst=True)
    threat_analysis_run_status.create(bind, checkfirst=True)
    threat_finding_status.create(bind, checkfirst=True)
    threat_category.create(bind, checkfirst=True)

    op.create_table(
        "threat_models",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("system_type", sa.String(length=64), nullable=False),
        sa.Column("status", threat_model_status, nullable=False),
        sa.Column("architecture", sa.JSON(), nullable=False),
        sa.Column("architecture_digest", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("version >= 1", name="ck_threat_models_version_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_models_name", "threat_models", ["name"], unique=False)
    op.create_index(
        "ix_threat_models_architecture_digest",
        "threat_models",
        ["architecture_digest"],
        unique=False,
    )

    op.create_table(
        "threat_analysis_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("threat_model_id", sa.String(length=36), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("status", threat_analysis_run_status, nullable=False),
        sa.Column("engine_version", sa.String(length=64), nullable=False),
        sa.Column("input_digest", sa.String(length=64), nullable=False),
        sa.Column("rules_digest", sa.String(length=64), nullable=False),
        sa.Column("finding_count", sa.Integer(), nullable=False),
        sa.Column("max_risk_score", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "finding_count >= 0", name="ck_threat_runs_finding_count_nonnegative"
        ),
        sa.CheckConstraint(
            "max_risk_score >= 0 AND max_risk_score <= 100",
            name="ck_threat_runs_max_risk_range",
        ),
        sa.ForeignKeyConstraint(
            ["threat_model_id"], ["threat_models.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        "ix_threat_analysis_runs_threat_model_id",
        "threat_analysis_runs",
        ["threat_model_id"],
        unique=False,
    )
    op.create_index(
        "ix_threat_analysis_runs_request_id",
        "threat_analysis_runs",
        ["request_id"],
        unique=True,
    )

    op.create_table(
        "threat_findings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("threat_model_id", sa.String(length=36), nullable=False),
        sa.Column("analysis_run_id", sa.String(length=36), nullable=False),
        sa.Column("rule_id", sa.String(length=64), nullable=False),
        sa.Column("category", threat_category, nullable=False),
        sa.Column("status", threat_finding_status, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("scenario", sa.Text(), nullable=False),
        sa.Column("asset", sa.String(length=255), nullable=False),
        sa.Column("component_id", sa.String(length=128), nullable=True),
        sa.Column("trust_boundary", sa.String(length=255), nullable=True),
        sa.Column("likelihood", sa.Integer(), nullable=False),
        sa.Column("impact", sa.Integer(), nullable=False),
        sa.Column("exposure", sa.Integer(), nullable=False),
        sa.Column("control_gap", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("mitigations", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "likelihood BETWEEN 1 AND 5", name="ck_threat_findings_likelihood"
        ),
        sa.CheckConstraint("impact BETWEEN 1 AND 5", name="ck_threat_findings_impact"),
        sa.CheckConstraint("exposure BETWEEN 1 AND 5", name="ck_threat_findings_exposure"),
        sa.CheckConstraint(
            "control_gap BETWEEN 1 AND 5", name="ck_threat_findings_control_gap"
        ),
        sa.CheckConstraint(
            "risk_score BETWEEN 0 AND 100", name="ck_threat_findings_risk_range"
        ),
        sa.ForeignKeyConstraint(
            ["analysis_run_id"], ["threat_analysis_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["threat_model_id"], ["threat_models.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_threat_findings_threat_model_id",
        "threat_findings",
        ["threat_model_id"],
        unique=False,
    )
    op.create_index(
        "ix_threat_findings_analysis_run_id",
        "threat_findings",
        ["analysis_run_id"],
        unique=False,
    )
    op.create_index(
        "ix_threat_findings_category", "threat_findings", ["category"], unique=False
    )
    op.create_index(
        "ix_threat_findings_component_id",
        "threat_findings",
        ["component_id"],
        unique=False,
    )
    op.create_index(
        "ix_threat_findings_risk_score",
        "threat_findings",
        ["risk_score"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_threat_findings_risk_score", table_name="threat_findings")
    op.drop_index("ix_threat_findings_component_id", table_name="threat_findings")
    op.drop_index("ix_threat_findings_category", table_name="threat_findings")
    op.drop_index("ix_threat_findings_analysis_run_id", table_name="threat_findings")
    op.drop_index("ix_threat_findings_threat_model_id", table_name="threat_findings")
    op.drop_table("threat_findings")
    op.drop_index("ix_threat_analysis_runs_request_id", table_name="threat_analysis_runs")
    op.drop_index("ix_threat_analysis_runs_threat_model_id", table_name="threat_analysis_runs")
    op.drop_table("threat_analysis_runs")
    op.drop_index("ix_threat_models_architecture_digest", table_name="threat_models")
    op.drop_index("ix_threat_models_name", table_name="threat_models")
    op.drop_table("threat_models")

    bind = op.get_bind()
    threat_category.drop(bind, checkfirst=True)
    threat_finding_status.drop(bind, checkfirst=True)
    threat_analysis_run_status.drop(bind, checkfirst=True)
    threat_model_status.drop(bind, checkfirst=True)
