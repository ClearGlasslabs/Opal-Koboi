from __future__ import annotations

from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.event import Event
from app.models.threat_model import ThreatCategory, ThreatModelStatus
from app.schemas.threat_model import (
    ArchitectureComponent,
    ArchitectureDataFlow,
    ArchitectureTrustBoundary,
    ComponentKind,
    DataClassification,
    ThreatArchitecture,
    ThreatModelAnalyze,
    ThreatModelCreate,
)
from app.services.threat_engine import ENGINE_VERSION, RULES_DIGEST, analyze_architecture
from app.services.threat_model_service import analyze_threat_model, create_threat_model


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session


def representative_architecture() -> ThreatArchitecture:
    return ThreatArchitecture(
        components=[
            ArchitectureComponent(
                id="public-ingress",
                name="Public Intake Gateway",
                kind=ComponentKind.api,
                trust_zone="internet",
                data_classification=DataClassification.confidential,
                internet_exposed=True,
                authentication=False,
                audit_logging=False,
                rate_limiting=False,
                accepts_untrusted_input=True,
                encryption_at_rest=False,
                dependencies=["gateway-image@sha256:example"],
            ),
            ArchitectureComponent(
                id="planner-agent",
                name="Planner Agent",
                kind=ComponentKind.agent,
                trust_zone="agent-plane",
                data_classification=DataClassification.regulated,
                authorization=False,
                accepts_untrusted_input=True,
                executes_tools=True,
                persistent_memory=True,
                dependencies=["foundation-model:v1"],
            ),
            ArchitectureComponent(
                id="review-agent",
                name="Review Agent",
                kind=ComponentKind.agent,
                trust_zone="agent-plane",
                data_classification=DataClassification.internal,
            ),
            ArchitectureComponent(
                id="sensor-fusion",
                name="Sensor Fusion",
                kind=ComponentKind.sensor,
                trust_zone="ot-zone",
                data_classification=DataClassification.mission_critical,
                receives_sensor_data=True,
            ),
            ArchitectureComponent(
                id="actuator-control",
                name="Actuator Controller",
                kind=ComponentKind.actuator,
                trust_zone="ot-zone",
                data_classification=DataClassification.mission_critical,
                controls_physical_process=True,
                authorization=False,
            ),
        ],
        trust_boundaries=[
            ArchitectureTrustBoundary(
                id="internet-to-agent",
                name="Internet to Agent Plane",
                source_zone="internet",
                target_zone="agent-plane",
            ),
            ArchitectureTrustBoundary(
                id="agent-to-ot",
                name="Agent Plane to OT",
                source_zone="agent-plane",
                target_zone="ot-zone",
                boundary_type="it-ot",
            ),
        ],
        data_flows=[
            ArchitectureDataFlow(
                id="ingress-to-planner",
                source="public-ingress",
                target="planner-agent",
                protocol="https",
                data_classification=DataClassification.confidential,
                crosses_trust_boundary=True,
                trust_boundary="internet-to-agent",
                authenticated=False,
                encrypted=False,
            ),
            ArchitectureDataFlow(
                id="planner-to-review",
                source="planner-agent",
                target="review-agent",
                protocol="agent-message",
                data_classification=DataClassification.regulated,
            ),
            ArchitectureDataFlow(
                id="planner-to-actuator",
                source="planner-agent",
                target="actuator-control",
                protocol="command-bus",
                data_classification=DataClassification.mission_critical,
                crosses_trust_boundary=True,
                trust_boundary="agent-to-ot",
                authenticated=True,
                encrypted=True,
            ),
        ],
        metadata={"environment": "test", "owner": "ClearGlass"},
    )


def test_engine_detects_agentic_and_cyber_physical_risks_deterministically() -> None:
    architecture = representative_architecture()
    first = analyze_architecture(architecture)
    second = analyze_architecture(architecture)

    assert first == second
    assert [finding.risk_score for finding in first] == sorted(
        [finding.risk_score for finding in first], reverse=True
    )
    assert all(0 <= finding.risk_score <= 100 for finding in first)

    categories = {finding.category for finding in first}
    assert ThreatCategory.spoofing in categories
    assert ThreatCategory.prompt_injection in categories
    assert ThreatCategory.tool_abuse in categories
    assert ThreatCategory.memory_poisoning in categories
    assert ThreatCategory.agent_collusion in categories
    assert ThreatCategory.sensor_spoofing in categories
    assert ThreatCategory.actuator_hijacking in categories
    assert ThreatCategory.supply_chain in categories
    assert ThreatCategory.information_disclosure in categories
    assert ThreatCategory.tampering in categories


def test_analysis_persists_provenance_findings_and_audit_chain(db: Session) -> None:
    architecture = representative_architecture()
    model = create_threat_model(
        db,
        ThreatModelCreate(
            actor="security-architect",
            request_id="threat-create-0001",
            name="Critical Autonomous Platform",
            description="Agentic and cyber-physical reference architecture",
            system_type="cyber-physical-autonomous",
            architecture=architecture,
        ),
    )
    assert model.status is ThreatModelStatus.draft
    assert model.version == 1

    model, run, findings = analyze_threat_model(
        db,
        model.id,
        ThreatModelAnalyze(
            actor="security-architect",
            request_id="threat-analyze-0001",
            expected_version=1,
        ),
    )

    assert model.status is ThreatModelStatus.analyzed
    assert model.version == 2
    assert run.engine_version == ENGINE_VERSION
    assert run.rules_digest == RULES_DIGEST
    assert run.finding_count == len(findings)
    assert run.max_risk_score == max(finding.risk_score for finding in findings)
    assert all(finding.analysis_run_id == run.id for finding in findings)
    assert all(finding.evidence for finding in findings)
    assert all(finding.mitigations for finding in findings)

    events = list(db.scalars(select(Event)))
    create_event = next(event for event in events if event.action == "threat_model.create")
    analysis_event = next(event for event in events if event.action == "threat_model.analyze")
    assert analysis_event.previous_hash == create_event.event_hash
    assert analysis_event.payload["rules_digest"] == RULES_DIGEST
    assert analysis_event.payload["finding_count"] == len(findings)


def test_analysis_enforces_idempotency_and_optimistic_versioning(db: Session) -> None:
    model = create_threat_model(
        db,
        ThreatModelCreate(
            actor="operator",
            request_id="threat-create-1001",
            name="Autonomous Service",
            system_type="agentic-software",
            architecture=representative_architecture(),
        ),
    )

    with pytest.raises(HTTPException) as stale:
        analyze_threat_model(
            db,
            model.id,
            ThreatModelAnalyze(
                actor="operator",
                request_id="threat-analyze-stale",
                expected_version=99,
            ),
        )
    assert stale.value.status_code == 409

    analyze_threat_model(
        db,
        model.id,
        ThreatModelAnalyze(
            actor="operator",
            request_id="threat-analyze-1001",
            expected_version=1,
        ),
    )

    with pytest.raises(HTTPException) as duplicate:
        analyze_threat_model(
            db,
            model.id,
            ThreatModelAnalyze(
                actor="operator",
                request_id="threat-analyze-1001",
                expected_version=2,
            ),
        )
    assert duplicate.value.status_code == 409
