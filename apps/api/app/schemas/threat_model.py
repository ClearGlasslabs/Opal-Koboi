from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.threat_model import (
    AnalysisRunStatus,
    ThreatCategory,
    ThreatFindingStatus,
    ThreatModelStatus,
)
from app.schemas.common import ActorContext


class ComponentKind(str, enum.Enum):
    service = "service"
    database = "database"
    api = "api"
    agent = "agent"
    model = "model"
    orchestrator = "orchestrator"
    memory = "memory"
    sensor = "sensor"
    actuator = "actuator"
    identity_provider = "identity_provider"
    external_system = "external_system"
    user_interface = "user_interface"


class DataClassification(str, enum.Enum):
    public = "public"
    internal = "internal"
    confidential = "confidential"
    regulated = "regulated"
    mission_critical = "mission_critical"


class ArchitectureComponent(BaseModel):
    id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    name: str = Field(min_length=1, max_length=255)
    kind: ComponentKind
    trust_zone: str = Field(min_length=1, max_length=128)
    data_classification: DataClassification = DataClassification.internal
    internet_exposed: bool = False
    authentication: bool = True
    authorization: bool = True
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    audit_logging: bool = True
    rate_limiting: bool = True
    accepts_untrusted_input: bool = False
    executes_tools: bool = False
    persistent_memory: bool = False
    receives_sensor_data: bool = False
    controls_physical_process: bool = False
    dependencies: list[str] = Field(default_factory=list, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArchitectureDataFlow(BaseModel):
    id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    source: str = Field(min_length=1, max_length=128)
    target: str = Field(min_length=1, max_length=128)
    protocol: str = Field(min_length=1, max_length=64)
    data_classification: DataClassification = DataClassification.internal
    crosses_trust_boundary: bool = False
    trust_boundary: str | None = Field(default=None, max_length=255)
    authenticated: bool = True
    encrypted: bool = True
    unidirectional: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArchitectureTrustBoundary(BaseModel):
    id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    name: str = Field(min_length=1, max_length=255)
    source_zone: str = Field(min_length=1, max_length=128)
    target_zone: str = Field(min_length=1, max_length=128)
    boundary_type: str = Field(default="network", min_length=1, max_length=64)


class ThreatArchitecture(BaseModel):
    components: list[ArchitectureComponent] = Field(min_length=1, max_length=500)
    data_flows: list[ArchitectureDataFlow] = Field(default_factory=list, max_length=2000)
    trust_boundaries: list[ArchitectureTrustBoundary] = Field(default_factory=list, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_graph(self) -> "ThreatArchitecture":
        component_ids = [component.id for component in self.components]
        if len(component_ids) != len(set(component_ids)):
            raise ValueError("component ids must be unique")

        flow_ids = [flow.id for flow in self.data_flows]
        if len(flow_ids) != len(set(flow_ids)):
            raise ValueError("data-flow ids must be unique")

        boundary_ids = [boundary.id for boundary in self.trust_boundaries]
        if len(boundary_ids) != len(set(boundary_ids)):
            raise ValueError("trust-boundary ids must be unique")

        known_components = set(component_ids)
        known_boundaries = set(boundary_ids)
        for flow in self.data_flows:
            if flow.source not in known_components or flow.target not in known_components:
                raise ValueError(f"data flow {flow.id} references an unknown component")
            if flow.trust_boundary and flow.trust_boundary not in known_boundaries:
                raise ValueError(f"data flow {flow.id} references an unknown trust boundary")
        return self


class ThreatModelCreate(ActorContext):
    name: str = Field(min_length=3, max_length=255)
    description: str = Field(default="", max_length=20000)
    system_type: str = Field(default="software", min_length=2, max_length=64)
    architecture: ThreatArchitecture


class ThreatModelAnalyze(ActorContext):
    expected_version: int = Field(ge=1)


class ThreatModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    system_type: str
    status: ThreatModelStatus
    architecture: ThreatArchitecture
    architecture_digest: str
    version: int
    created_by: str
    created_at: datetime
    updated_at: datetime


class ThreatAnalysisRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    threat_model_id: str
    request_id: str
    actor: str
    status: AnalysisRunStatus
    engine_version: str
    input_digest: str
    rules_digest: str
    finding_count: int
    max_risk_score: int
    created_at: datetime


class ThreatFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    threat_model_id: str
    analysis_run_id: str
    rule_id: str
    category: ThreatCategory
    status: ThreatFindingStatus
    title: str
    scenario: str
    asset: str
    component_id: str | None
    trust_boundary: str | None
    likelihood: int
    impact: int
    exposure: int
    control_gap: int
    risk_score: int
    evidence: dict[str, Any]
    mitigations: list[str]
    created_at: datetime


class ThreatAnalysisResult(BaseModel):
    threat_model: ThreatModelRead
    run: ThreatAnalysisRunRead
    findings: list[ThreatFindingRead]
