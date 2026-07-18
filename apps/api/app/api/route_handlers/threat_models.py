from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.dependencies import Authorized, DbSession
from app.schemas.threat_model import (
    ThreatAnalysisResult,
    ThreatAnalysisRunRead,
    ThreatFindingRead,
    ThreatModelAnalyze,
    ThreatModelCreate,
    ThreatModelRead,
)
from app.services.threat_model_service import (
    analyze_threat_model,
    create_threat_model,
    get_threat_model_or_404,
    list_findings,
    list_models,
    list_runs,
)

router = APIRouter(prefix="/threat-models", tags=["threat-modeling"])


@router.get("", response_model=list[ThreatModelRead])
def read_threat_models(
    _: Authorized,
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
):
    return list_models(db, limit=limit)


@router.post("", response_model=ThreatModelRead, status_code=201)
def add_threat_model(command: ThreatModelCreate, _: Authorized, db: DbSession):
    return create_threat_model(db, command)


@router.get("/{threat_model_id}", response_model=ThreatModelRead)
def read_threat_model(threat_model_id: str, _: Authorized, db: DbSession):
    return get_threat_model_or_404(db, threat_model_id)


@router.post("/{threat_model_id}/analyze", response_model=ThreatAnalysisResult)
def run_threat_analysis(
    threat_model_id: str,
    command: ThreatModelAnalyze,
    _: Authorized,
    db: DbSession,
):
    model, run, findings = analyze_threat_model(db, threat_model_id, command)
    return ThreatAnalysisResult(threat_model=model, run=run, findings=findings)


@router.get("/{threat_model_id}/runs", response_model=list[ThreatAnalysisRunRead])
def read_analysis_runs(
    threat_model_id: str,
    _: Authorized,
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
):
    get_threat_model_or_404(db, threat_model_id)
    return list_runs(db, threat_model_id=threat_model_id, limit=limit)


@router.get("/{threat_model_id}/findings", response_model=list[ThreatFindingRead])
def read_threat_findings(
    threat_model_id: str,
    _: Authorized,
    db: DbSession,
    analysis_run_id: str | None = None,
    minimum_risk: int = Query(default=0, ge=0, le=100),
    limit: int = Query(default=500, ge=1, le=2000),
):
    get_threat_model_or_404(db, threat_model_id)
    return list_findings(
        db,
        threat_model_id=threat_model_id,
        analysis_run_id=analysis_run_id,
        minimum_risk=minimum_risk,
        limit=limit,
    )
