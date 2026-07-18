from __future__ import annotations

from collections import Counter

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.event import get_event_by_request_id
from app.crud.threat_model import (
    create_findings,
    create_model,
    create_run,
    get_model,
    get_run_by_request_id,
    list_findings,
    list_models,
    list_runs,
)
from app.models.threat_model import (
    AnalysisRunStatus,
    ThreatAnalysisRun,
    ThreatFinding,
    ThreatModel,
    ThreatModelStatus,
)
from app.schemas.threat_model import ThreatArchitecture, ThreatModelAnalyze, ThreatModelCreate
from app.services.audit_service import append_event
from app.services.threat_engine import (
    ENGINE_VERSION,
    RULES_DIGEST,
    analyze_architecture,
    architecture_digest,
)


def get_threat_model_or_404(db: Session, threat_model_id: str) -> ThreatModel:
    model = get_model(db, threat_model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat model not found")
    return model


def create_threat_model(db: Session, command: ThreatModelCreate) -> ThreatModel:
    if get_event_by_request_id(db, command.request_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="request_id already processed")

    architecture_payload = command.architecture.model_dump(mode="json")
    model = create_model(
        db,
        ThreatModel(
            name=command.name,
            description=command.description,
            system_type=command.system_type,
            architecture=architecture_payload,
            architecture_digest=architecture_digest(command.architecture),
            created_by=command.actor,
        ),
    )
    append_event(
        db,
        request_id=command.request_id,
        actor=command.actor,
        action="threat_model.create",
        target=f"threat_model:{model.id}",
        payload={
            "name": model.name,
            "system_type": model.system_type,
            "architecture_digest": model.architecture_digest,
            "component_count": len(command.architecture.components),
            "data_flow_count": len(command.architecture.data_flows),
        },
        result="created",
        risk_score=10,
    )
    return model


def analyze_threat_model(
    db: Session,
    threat_model_id: str,
    command: ThreatModelAnalyze,
) -> tuple[ThreatModel, ThreatAnalysisRun, list[ThreatFinding]]:
    model = get_threat_model_or_404(db, threat_model_id)
    if model.status is ThreatModelStatus.archived:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Threat model is archived")
    if model.version != command.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Version conflict", "current_version": model.version},
        )
    if get_run_by_request_id(db, command.request_id) or get_event_by_request_id(
        db, command.request_id
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="request_id already processed")

    architecture = ThreatArchitecture.model_validate(model.architecture)
    input_digest = architecture_digest(architecture)
    if input_digest != model.architecture_digest:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stored architecture digest does not match the validated architecture",
        )

    proposed = analyze_architecture(architecture)
    max_risk = max((finding.risk_score for finding in proposed), default=0)
    run = create_run(
        db,
        ThreatAnalysisRun(
            threat_model_id=model.id,
            request_id=command.request_id,
            actor=command.actor,
            status=AnalysisRunStatus.completed,
            engine_version=ENGINE_VERSION,
            input_digest=input_digest,
            rules_digest=RULES_DIGEST,
            finding_count=len(proposed),
            max_risk_score=max_risk,
        ),
    )
    findings = create_findings(
        db,
        threat_model_id=model.id,
        analysis_run_id=run.id,
        findings=proposed,
    )

    model.status = ThreatModelStatus.analyzed
    model.version += 1
    categories = Counter(finding.category.value for finding in proposed)
    append_event(
        db,
        request_id=command.request_id,
        actor=command.actor,
        action="threat_model.analyze",
        target=f"threat_model:{model.id}",
        payload={
            "analysis_run_id": run.id,
            "engine_version": ENGINE_VERSION,
            "rules_digest": RULES_DIGEST,
            "input_digest": input_digest,
            "finding_count": len(proposed),
            "max_risk_score": max_risk,
            "categories": dict(sorted(categories.items())),
        },
        result="completed",
        risk_score=max_risk,
    )
    db.flush()
    return model, run, findings


__all__ = [
    "analyze_threat_model",
    "create_threat_model",
    "get_threat_model_or_404",
    "list_findings",
    "list_models",
    "list_runs",
]
