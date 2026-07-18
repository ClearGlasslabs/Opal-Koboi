from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import new_id


class ThreatModelStatus(str, enum.Enum):
    draft = "draft"
    analyzed = "analyzed"
    archived = "archived"


class AnalysisRunStatus(str, enum.Enum):
    completed = "completed"
    failed = "failed"


class ThreatFindingStatus(str, enum.Enum):
    open = "open"
    accepted = "accepted"
    mitigated = "mitigated"
    false_positive = "false_positive"


class ThreatCategory(str, enum.Enum):
    spoofing = "spoofing"
    tampering = "tampering"
    repudiation = "repudiation"
    information_disclosure = "information_disclosure"
    denial_of_service = "denial_of_service"
    elevation_of_privilege = "elevation_of_privilege"
    prompt_injection = "prompt_injection"
    tool_abuse = "tool_abuse"
    memory_poisoning = "memory_poisoning"
    agent_collusion = "agent_collusion"
    sensor_spoofing = "sensor_spoofing"
    actuator_hijacking = "actuator_hijacking"
    supply_chain = "supply_chain"


class ThreatModel(Base):
    __tablename__ = "threat_models"
    __table_args__ = (CheckConstraint("version >= 1", name="ck_threat_models_version_positive"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    system_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[ThreatModelStatus] = mapped_column(
        Enum(ThreatModelStatus, name="threat_model_status"),
        nullable=False,
        default=ThreatModelStatus.draft,
    )
    architecture: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    architecture_digest: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ThreatAnalysisRun(Base):
    __tablename__ = "threat_analysis_runs"
    __table_args__ = (
        CheckConstraint("finding_count >= 0", name="ck_threat_runs_finding_count_nonnegative"),
        CheckConstraint(
            "max_risk_score >= 0 AND max_risk_score <= 100",
            name="ck_threat_runs_max_risk_range",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    threat_model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("threat_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    request_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AnalysisRunStatus] = mapped_column(
        Enum(AnalysisRunStatus, name="threat_analysis_run_status"),
        nullable=False,
        default=AnalysisRunStatus.completed,
    )
    engine_version: Mapped[str] = mapped_column(String(64), nullable=False)
    input_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    rules_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    finding_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ThreatFinding(Base):
    __tablename__ = "threat_findings"
    __table_args__ = (
        CheckConstraint("likelihood BETWEEN 1 AND 5", name="ck_threat_findings_likelihood"),
        CheckConstraint("impact BETWEEN 1 AND 5", name="ck_threat_findings_impact"),
        CheckConstraint("exposure BETWEEN 1 AND 5", name="ck_threat_findings_exposure"),
        CheckConstraint("control_gap BETWEEN 1 AND 5", name="ck_threat_findings_control_gap"),
        CheckConstraint("risk_score BETWEEN 0 AND 100", name="ck_threat_findings_risk_range"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    threat_model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("threat_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analysis_run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("threat_analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[ThreatCategory] = mapped_column(
        Enum(ThreatCategory, name="threat_category"), nullable=False, index=True
    )
    status: Mapped[ThreatFindingStatus] = mapped_column(
        Enum(ThreatFindingStatus, name="threat_finding_status"),
        nullable=False,
        default=ThreatFindingStatus.open,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario: Mapped[str] = mapped_column(Text, nullable=False)
    asset: Mapped[str] = mapped_column(String(255), nullable=False)
    component_id: Mapped[str | None] = mapped_column(String(128), index=True)
    trust_boundary: Mapped[str | None] = mapped_column(String(255))
    likelihood: Mapped[int] = mapped_column(Integer, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)
    exposure: Mapped[int] = mapped_column(Integer, nullable=False)
    control_gap: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    mitigations: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
