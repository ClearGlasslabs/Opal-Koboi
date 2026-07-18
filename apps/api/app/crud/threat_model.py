from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.threat_model import ThreatAnalysisRun, ThreatFinding, ThreatModel
from app.services.threat_engine import ProposedFinding


def create_model(db: Session, model: ThreatModel) -> ThreatModel:
    db.add(model)
    db.flush()
    return model


def get_model(db: Session, threat_model_id: str) -> ThreatModel | None:
    return db.get(ThreatModel, threat_model_id)


def list_models(db: Session, *, limit: int = 100) -> list[ThreatModel]:
    statement = select(ThreatModel).order_by(ThreatModel.updated_at.desc()).limit(limit)
    return list(db.scalars(statement))


def get_run_by_request_id(db: Session, request_id: str) -> ThreatAnalysisRun | None:
    return db.scalar(
        select(ThreatAnalysisRun).where(ThreatAnalysisRun.request_id == request_id).limit(1)
    )


def create_run(db: Session, run: ThreatAnalysisRun) -> ThreatAnalysisRun:
    db.add(run)
    db.flush()
    return run


def create_findings(
    db: Session,
    *,
    threat_model_id: str,
    analysis_run_id: str,
    findings: Iterable[ProposedFinding],
) -> list[ThreatFinding]:
    persisted = [
        ThreatFinding(
            threat_model_id=threat_model_id,
            analysis_run_id=analysis_run_id,
            rule_id=finding.rule_id,
            category=finding.category,
            title=finding.title,
            scenario=finding.scenario,
            asset=finding.asset,
            component_id=finding.component_id,
            trust_boundary=finding.trust_boundary,
            likelihood=finding.likelihood,
            impact=finding.impact,
            exposure=finding.exposure,
            control_gap=finding.control_gap,
            risk_score=finding.risk_score,
            evidence=finding.evidence,
            mitigations=list(finding.mitigations),
        )
        for finding in findings
    ]
    db.add_all(persisted)
    db.flush()
    return persisted


def list_runs(db: Session, *, threat_model_id: str, limit: int = 100) -> list[ThreatAnalysisRun]:
    statement = (
        select(ThreatAnalysisRun)
        .where(ThreatAnalysisRun.threat_model_id == threat_model_id)
        .order_by(ThreatAnalysisRun.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(statement))


def list_findings(
    db: Session,
    *,
    threat_model_id: str,
    analysis_run_id: str | None = None,
    minimum_risk: int = 0,
    limit: int = 500,
) -> list[ThreatFinding]:
    statement = select(ThreatFinding).where(
        ThreatFinding.threat_model_id == threat_model_id,
        ThreatFinding.risk_score >= minimum_risk,
    )
    if analysis_run_id:
        statement = statement.where(ThreatFinding.analysis_run_id == analysis_run_id)
    statement = statement.order_by(ThreatFinding.risk_score.desc(), ThreatFinding.created_at.desc())
    return list(db.scalars(statement.limit(limit)))
