from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable

from app.models.threat_model import ThreatCategory
from app.schemas.threat_model import (
    ArchitectureComponent,
    ArchitectureDataFlow,
    ComponentKind,
    DataClassification,
    ThreatArchitecture,
)

ENGINE_VERSION = "clearglass-atm-2026.1"

RULE_IDS = (
    "ATM-AUTH-001",
    "ATM-AUTHZ-002",
    "ATM-PROMPT-003",
    "ATM-MEMORY-004",
    "ATM-AUDIT-005",
    "ATM-DOS-006",
    "ATM-DATA-007",
    "ATM-SUPPLY-008",
    "ATM-SENSOR-009",
    "ATM-ACTUATOR-010",
    "ATM-FLOW-011",
    "ATM-FLOW-012",
    "ATM-AGENT-013",
    "ATM-AGENT-014",
)
RULES_DIGEST = hashlib.sha256("\n".join(RULE_IDS).encode("utf-8")).hexdigest()

AGENT_KINDS = {ComponentKind.agent, ComponentKind.model, ComponentKind.orchestrator}
HIGH_VALUE_DATA = {
    DataClassification.confidential,
    DataClassification.regulated,
    DataClassification.mission_critical,
}


@dataclass(frozen=True, slots=True)
class ProposedFinding:
    rule_id: str
    category: ThreatCategory
    title: str
    scenario: str
    asset: str
    component_id: str | None
    trust_boundary: str | None
    likelihood: int
    impact: int
    exposure: int
    control_gap: int
    evidence: dict[str, Any]
    mitigations: tuple[str, ...]

    @property
    def risk_score(self) -> int:
        # Weighted 0-100 score: consequence dominates, while exposure and control
        # weakness determine how urgently the scenario should be remediated.
        consequence = (self.likelihood * self.impact / 25) * 60
        reachability = (self.exposure / 5) * 20
        weakness = (self.control_gap / 5) * 20
        return min(100, max(0, round(consequence + reachability + weakness)))

    @property
    def stable_key(self) -> tuple[str, str | None, str | None, str]:
        return (self.rule_id, self.component_id, self.trust_boundary, self.asset)


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def architecture_digest(architecture: ThreatArchitecture) -> str:
    return canonical_digest(architecture.model_dump(mode="json"))


def _exposure(component: ArchitectureComponent) -> int:
    if component.internet_exposed:
        return 5
    if component.accepts_untrusted_input:
        return 4
    return 2


def _classification_impact(classification: DataClassification) -> int:
    return {
        DataClassification.public: 1,
        DataClassification.internal: 2,
        DataClassification.confidential: 4,
        DataClassification.regulated: 5,
        DataClassification.mission_critical: 5,
    }[classification]


def _finding(
    *,
    rule_id: str,
    category: ThreatCategory,
    title: str,
    scenario: str,
    asset: str,
    component: ArchitectureComponent | None = None,
    flow: ArchitectureDataFlow | None = None,
    likelihood: int,
    impact: int,
    exposure: int,
    control_gap: int,
    evidence: dict[str, Any],
    mitigations: Iterable[str],
) -> ProposedFinding:
    return ProposedFinding(
        rule_id=rule_id,
        category=category,
        title=title,
        scenario=scenario,
        asset=asset,
        component_id=component.id if component else None,
        trust_boundary=flow.trust_boundary if flow else None,
        likelihood=likelihood,
        impact=impact,
        exposure=exposure,
        control_gap=control_gap,
        evidence=evidence,
        mitigations=tuple(mitigations),
    )


def _component_findings(component: ArchitectureComponent) -> list[ProposedFinding]:
    findings: list[ProposedFinding] = []
    exposure = _exposure(component)
    impact = _classification_impact(component.data_classification)

    if component.internet_exposed and not component.authentication:
        findings.append(
            _finding(
                rule_id="ATM-AUTH-001",
                category=ThreatCategory.spoofing,
                title=f"Unauthenticated identity boundary on {component.name}",
                scenario=(
                    "An external actor can present an unverified identity to an internet-reachable "
                    "component and impersonate a trusted user, service, device, or agent."
                ),
                asset=component.name,
                component=component,
                likelihood=5,
                impact=max(impact, 4),
                exposure=5,
                control_gap=5,
                evidence={"internet_exposed": True, "authentication": False},
                mitigations=(
                    "Require phishing-resistant user or workload authentication at the boundary.",
                    "Bind credentials to audience, workload identity, and short expiration windows.",
                    "Reject anonymous requests before application or model execution.",
                ),
            )
        )

    if component.executes_tools and not component.authorization:
        findings.append(
            _finding(
                rule_id="ATM-AUTHZ-002",
                category=ThreatCategory.tool_abuse,
                title=f"Tool execution lacks an independent authorization gate on {component.name}",
                scenario=(
                    "A compromised or misdirected agent can invoke tools beyond the operator's intent "
                    "because tool availability is not constrained by server-side authorization."
                ),
                asset=component.name,
                component=component,
                likelihood=4,
                impact=5,
                exposure=exposure,
                control_gap=5,
                evidence={"executes_tools": True, "authorization": False},
                mitigations=(
                    "Enforce typed, resource-scoped tool authorization outside the model.",
                    "Separate planning, approval, execution, and audit identities.",
                    "Require human approval for consequential or irreversible tools.",
                ),
            )
        )

    if component.accepts_untrusted_input and component.executes_tools:
        findings.append(
            _finding(
                rule_id="ATM-PROMPT-003",
                category=ThreatCategory.prompt_injection,
                title=f"Untrusted input can influence tool-capable component {component.name}",
                scenario=(
                    "Hostile content can manipulate instructions, retrieved context, or agent planning "
                    "and produce unauthorized tool proposals or data disclosure attempts."
                ),
                asset=component.name,
                component=component,
                likelihood=5,
                impact=5 if component.controls_physical_process else 4,
                exposure=max(exposure, 4),
                control_gap=4 if component.authorization else 3,
                evidence={
                    "accepts_untrusted_input": True,
                    "executes_tools": True,
                    "authorization": component.authorization,
                },
                mitigations=(
                    "Treat retrieved and user-supplied content as untrusted data, never authority.",
                    "Apply deterministic policy checks to every proposed tool invocation.",
                    "Use taint-aware egress restrictions and approval escalation for risky sessions.",
                ),
            )
        )

    if component.accepts_untrusted_input and component.persistent_memory:
        findings.append(
            _finding(
                rule_id="ATM-MEMORY-004",
                category=ThreatCategory.memory_poisoning,
                title=f"Persistent memory can retain hostile instructions in {component.name}",
                scenario=(
                    "Malicious or low-integrity content can be stored as durable memory and silently "
                    "influence later tasks, users, agents, or decisions."
                ),
                asset=component.name,
                component=component,
                likelihood=4,
                impact=4,
                exposure=max(exposure, 4),
                control_gap=4,
                evidence={"accepts_untrusted_input": True, "persistent_memory": True},
                mitigations=(
                    "Record memory provenance, author, tenant, confidence, and expiration.",
                    "Quarantine untrusted memories until deterministic validation succeeds.",
                    "Provide operator review, revocation, and replay for memory mutations.",
                ),
            )
        )

    if not component.audit_logging:
        findings.append(
            _finding(
                rule_id="ATM-AUDIT-005",
                category=ThreatCategory.repudiation,
                title=f"Material actions are not attributable on {component.name}",
                scenario=(
                    "Operators cannot reliably reconstruct who or what initiated a consequential action, "
                    "which policy decided it, or what evidence supported the decision."
                ),
                asset=component.name,
                component=component,
                likelihood=3,
                impact=max(impact, 3),
                exposure=exposure,
                control_gap=5,
                evidence={"audit_logging": False},
                mitigations=(
                    "Write append-only, tamper-evident events for proposals, denials, approvals, and actions.",
                    "Record actor, model, prompt, policy, tool arguments, evidence, and result provenance.",
                    "Test audit-chain integrity and independent retention controls.",
                ),
            )
        )

    if component.internet_exposed and not component.rate_limiting:
        findings.append(
            _finding(
                rule_id="ATM-DOS-006",
                category=ThreatCategory.denial_of_service,
                title=f"Unbounded request pressure can exhaust {component.name}",
                scenario=(
                    "An attacker can consume compute, model tokens, downstream quotas, queues, or operator "
                    "attention faster than the system can recover."
                ),
                asset=component.name,
                component=component,
                likelihood=4,
                impact=max(impact, 3),
                exposure=5,
                control_gap=4,
                evidence={"internet_exposed": True, "rate_limiting": False},
                mitigations=(
                    "Enforce identity-aware quotas, bounded queues, timeouts, and cost budgets.",
                    "Apply circuit breakers and load shedding before downstream dependencies fail.",
                    "Alert on token, tool-call, queue-depth, and denial-rate anomalies.",
                ),
            )
        )

    if component.data_classification in HIGH_VALUE_DATA and not component.encryption_at_rest:
        findings.append(
            _finding(
                rule_id="ATM-DATA-007",
                category=ThreatCategory.information_disclosure,
                title=f"High-value data is stored without encryption in {component.name}",
                scenario=(
                    "Storage compromise, snapshot exposure, or misplaced media can disclose confidential, "
                    "regulated, or mission-critical data."
                ),
                asset=component.name,
                component=component,
                likelihood=3,
                impact=5,
                exposure=exposure,
                control_gap=5,
                evidence={
                    "data_classification": component.data_classification.value,
                    "encryption_at_rest": False,
                },
                mitigations=(
                    "Encrypt data with managed keys and documented rotation and revocation.",
                    "Minimize retained sensitive data and isolate tenant-specific key scope.",
                    "Test backup, export, cache, vector-store, and log encryption paths.",
                ),
            )
        )

    if component.dependencies:
        findings.append(
            _finding(
                rule_id="ATM-SUPPLY-008",
                category=ThreatCategory.supply_chain,
                title=f"Dependency compromise can alter {component.name}",
                scenario=(
                    "A compromised library, model, action, container, plugin, firmware package, or update "
                    "channel can introduce behavior outside the reviewed architecture."
                ),
                asset=component.name,
                component=component,
                likelihood=3,
                impact=max(impact, 4),
                exposure=exposure,
                control_gap=3,
                evidence={"dependencies": sorted(component.dependencies)},
                mitigations=(
                    "Pin reviewed dependencies and verify signatures, provenance, and immutable digests.",
                    "Generate an SBOM and maintain rapid dependency revocation and rollback procedures.",
                    "Isolate update channels and prevent untrusted build code from accessing production secrets.",
                ),
            )
        )

    if component.receives_sensor_data:
        findings.append(
            _finding(
                rule_id="ATM-SENSOR-009",
                category=ThreatCategory.sensor_spoofing,
                title=f"Sensor inputs can falsify the operating picture for {component.name}",
                scenario=(
                    "Forged, replayed, delayed, or physically manipulated sensor data can cause the system "
                    "to make unsafe or strategically incorrect decisions."
                ),
                asset=component.name,
                component=component,
                likelihood=4,
                impact=5 if component.controls_physical_process else 4,
                exposure=max(exposure, 3),
                control_gap=4,
                evidence={"receives_sensor_data": True},
                mitigations=(
                    "Authenticate sensor identity and integrity with anti-replay protection.",
                    "Cross-check independent modalities and reject implausible temporal or spatial states.",
                    "Define safe degraded behavior when confidence or sensor consensus falls below threshold.",
                ),
            )
        )

    if component.controls_physical_process:
        findings.append(
            _finding(
                rule_id="ATM-ACTUATOR-010",
                category=ThreatCategory.actuator_hijacking,
                title=f"Cyber decisions can produce physical effects through {component.name}",
                scenario=(
                    "A compromised command path, unsafe autonomous decision, or confused deputy can issue "
                    "an unauthorized physical action with safety, mission, or infrastructure consequences."
                ),
                asset=component.name,
                component=component,
                likelihood=3 if component.authorization else 4,
                impact=5,
                exposure=exposure,
                control_gap=3 if component.authorization and component.authentication else 5,
                evidence={
                    "controls_physical_process": True,
                    "authentication": component.authentication,
                    "authorization": component.authorization,
                },
                mitigations=(
                    "Place deterministic safety interlocks outside the autonomous decision path.",
                    "Require signed commands, bounded operating envelopes, and independent authorization.",
                    "Provide tested halt, manual takeover, rollback, and graceful-degradation modes.",
                ),
            )
        )

    return findings


def _flow_findings(
    flow: ArchitectureDataFlow,
    components: dict[str, ArchitectureComponent],
) -> list[ProposedFinding]:
    findings: list[ProposedFinding] = []
    source = components[flow.source]
    target = components[flow.target]
    flow_asset = f"{source.name} → {target.name}"
    impact = max(
        _classification_impact(flow.data_classification),
        _classification_impact(target.data_classification),
    )
    exposure = 5 if source.internet_exposed else 4 if source.accepts_untrusted_input else 3

    if flow.crosses_trust_boundary and not flow.encrypted:
        findings.append(
            _finding(
                rule_id="ATM-FLOW-011",
                category=ThreatCategory.information_disclosure,
                title=f"Unencrypted trust-boundary flow: {flow_asset}",
                scenario=(
                    "An observer or compromised intermediary can read or alter data while it crosses a "
                    "trust boundary."
                ),
                asset=flow_asset,
                component=target,
                flow=flow,
                likelihood=4,
                impact=max(impact, 3),
                exposure=exposure,
                control_gap=5,
                evidence={
                    "flow_id": flow.id,
                    "protocol": flow.protocol,
                    "crosses_trust_boundary": True,
                    "encrypted": False,
                },
                mitigations=(
                    "Require authenticated encryption for all trust-boundary traffic.",
                    "Validate certificate, service identity, audience, freshness, and protocol downgrade resistance.",
                    "Prevent sensitive values from entering protocols that cannot provide confidentiality.",
                ),
            )
        )

    if flow.crosses_trust_boundary and not flow.authenticated:
        findings.append(
            _finding(
                rule_id="ATM-FLOW-012",
                category=ThreatCategory.tampering,
                title=f"Unauthenticated trust-boundary flow: {flow_asset}",
                scenario=(
                    "A malicious intermediary can inject, replay, or replace messages because the receiver "
                    "cannot verify the sender or message integrity."
                ),
                asset=flow_asset,
                component=target,
                flow=flow,
                likelihood=4,
                impact=max(impact, 4),
                exposure=exposure,
                control_gap=5,
                evidence={
                    "flow_id": flow.id,
                    "protocol": flow.protocol,
                    "crosses_trust_boundary": True,
                    "authenticated": False,
                },
                mitigations=(
                    "Use mutually authenticated workload or device identities.",
                    "Bind messages to sender, recipient, timestamp, nonce, and integrity signature.",
                    "Reject replayed, stale, ambiguous, or duplicate commands.",
                ),
            )
        )

    if source.accepts_untrusted_input and target.executes_tools:
        findings.append(
            _finding(
                rule_id="ATM-AGENT-013",
                category=ThreatCategory.prompt_injection,
                title=f"Untrusted content reaches tool authority through {flow_asset}",
                scenario=(
                    "Content from an untrusted source can cross the flow and influence a component capable "
                    "of privileged tool execution."
                ),
                asset=flow_asset,
                component=target,
                flow=flow,
                likelihood=5,
                impact=5,
                exposure=max(exposure, 4),
                control_gap=4 if target.authorization else 5,
                evidence={
                    "flow_id": flow.id,
                    "source_accepts_untrusted_input": True,
                    "target_executes_tools": True,
                    "target_authorization": target.authorization,
                },
                mitigations=(
                    "Carry trust labels and provenance across the entire data-flow graph.",
                    "Prevent untrusted content from directly selecting tools, arguments, or destinations.",
                    "Escalate tainted sessions to read-only or human-approved execution.",
                ),
            )
        )

    if source.kind in AGENT_KINDS and target.kind in AGENT_KINDS:
        findings.append(
            _finding(
                rule_id="ATM-AGENT-014",
                category=ThreatCategory.agent_collusion,
                title=f"Agent-to-agent influence path: {flow_asset}",
                scenario=(
                    "Agents can reinforce erroneous assumptions, exchange poisoned context, or coordinate "
                    "around local controls unless authority and evidence are independently constrained."
                ),
                asset=flow_asset,
                component=target,
                flow=flow,
                likelihood=3,
                impact=4,
                exposure=exposure,
                control_gap=3,
                evidence={
                    "flow_id": flow.id,
                    "source_kind": source.kind.value,
                    "target_kind": target.kind.value,
                },
                mitigations=(
                    "Assign non-overlapping identities, capabilities, budgets, and mission scopes per agent.",
                    "Require provenance and independent policy evaluation at every agent handoff.",
                    "Detect circular delegation, consensus without evidence, and abnormal coordination patterns.",
                ),
            )
        )

    return findings


def analyze_architecture(architecture: ThreatArchitecture) -> list[ProposedFinding]:
    components = {component.id: component for component in architecture.components}
    proposed: list[ProposedFinding] = []
    for component in architecture.components:
        proposed.extend(_component_findings(component))
    for flow in architecture.data_flows:
        proposed.extend(_flow_findings(flow, components))

    deduplicated = {finding.stable_key: finding for finding in proposed}
    return sorted(
        deduplicated.values(),
        key=lambda finding: (
            -finding.risk_score,
            finding.category.value,
            finding.rule_id,
            finding.asset,
        ),
    )
