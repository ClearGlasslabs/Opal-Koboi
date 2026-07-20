# ClearGlassInc Artemis — Self-Evolving AI Intelligence Platform Implementation Blueprint

## Root cause / design driver

ClearGlassInc Artemis needs a production-grade architecture that lets mission operators use AI at machine speed without allowing autonomous, unreviewed changes to mission goals, permissions, workflows, or operational actions. The core design response is a governed full-stack system: Palantir Foundry provides integrated data and ontology, Gotham provides operational intelligence workflows, AIP provides copilots and tool-using agents, and Apollo controls signed deployment, canary rollout, rollback, and runtime policy.

## System Architecture

Palantir terminology used in this design:

- **Gotham**: operational intelligence, investigations, entity tracking, case work, link analysis, and mission command workflows.
- **Foundry**: data integration, transforms, ontology objects/actions, lineage, application logic, and operational data products.
- **AIP**: AI copilots, agent orchestration, tool execution, prompt/model governance, evaluations, and guarded workflow automation.
- **Apollo**: secure deployment, policy-aware rollout, rollback, runtime controls, edge updates, and release evidence.

### End-to-end control plane

| Layer | Purpose | Primary implementation | Palantir anchor |
| --- | --- | --- | --- |
| Frontend | Analyst cockpit, commander dashboard, case workbench, approval queues, eval review | Next.js, React, TypeScript, MapLibre, graph canvas, SSE/WebSocket streams | Gotham apps + Foundry apps |
| API gateway | Request normalization, auth context, rate limits, audit envelopes, BFF aggregation | Envoy/Kong, FastAPI BFF, OpenAPI, mTLS, signed request IDs | Foundry application logic |
| Backend services | Alerts, cases, missions, feedback, proposals, enrichment, action packages | Python FastAPI, Temporal, Postgres, Redis, worker pools | Gotham + Foundry services |
| Event bus | Live ingestion, normalized event fan-out, feedback, eval, release telemetry | Kafka/Pulsar/Redpanda topics with schema registry | Foundry streaming pipelines |
| Data layer | Historical and live data lakehouse, warehouse, curated datasets | Foundry datasets, Iceberg/Delta, SQL warehouse, object storage | Foundry |
| Ontology layer | Typed mission objects, links, actions, permissions, temporal state, lineage | Foundry Ontology object types, action types, object sets | Foundry Ontology + Gotham entity model |
| Retrieval layer | Keyword, vector, graph, geospatial, temporal retrieval | OpenSearch, governed vector index, graph queries, ontology APIs | Foundry + AIP tools |
| AI orchestration | Copilots, agents, tool registry, evals, prompt/model router, workflow state | AIP, LangGraph/Temporal-style workflows, model router | AIP |
| Policy layer | Need-to-know, coalition controls, row/column/entity/edge controls, approval gates | OPA/Rego, ABAC/RBAC/ReBAC, Foundry security, short-lived tool tokens | Foundry + AIP guardrails |
| Observability | Logs, traces, metrics, eval dashboards, audit trails, drift monitors | OpenTelemetry, Prometheus, Grafana, SIEM export, immutable append logs | Foundry telemetry + Apollo runtime |
| Deployment | Signed artifacts, staged rollout, canary, rollback, disconnected release channels | Apollo, SBOM, SLSA provenance, container signing, health gates | Apollo |

### Runtime lifecycle

```text
Source feeds
  -> Foundry ingestion connectors
  -> validation / schema checks / dedupe / classification
  -> normalized event topics
  -> ontology materialization
  -> policy-filtered object sets
  -> AIP triage/enrichment/correlation agents
  -> Gotham case and alert updates
  -> operator approval / rejection / correction
  -> feedback and outcome datasets
  -> eval suite generation
  -> human-reviewed improvement proposals
  -> Apollo canary rollout or rollback
```

### Primary services

```text
apps/web                Next.js mission UI and review consoles
apps/api                FastAPI gateway/BFF and public service surface
services/alert          alert lifecycle, dedupe, severity, state transitions
services/case           Gotham case sync, assignments, evidence bundles
services/ontology       permission-filtered ontology reads/actions
services/agent          AIP tool registry, workflow runner, model router
services/feedback       feedback capture, labels, eval case generation
services/governance     proposal review, approvals, release evidence
services/observability  audit, metrics, traces, drift detectors
infra/apollo            release gates, environments, rollback policy
policy                  Rego/Cedar-style policy bundles and tests
```

## Data and Ontology

The Foundry ontology is the system contract between humans, AI agents, apps, and audit. Agents do not query raw tables directly; they receive mission-scoped, policy-filtered ontology object sets and call governed ontology actions.

### Core ontology model

```yaml
Ontology:
  Mission:
    key: mission_id
    properties:
      name: string
      objective: string
      classification: enum[UNCLASSIFIED, PROTECTED, SECRET, TOP_SECRET]
      coalition_scope: string[]
      compartments: string[]
      approval_matrix_ref: string
      rules_of_engagement_ref: string
      start_time: timestamp
      end_time: timestamp?

  IntelEvent:
    key: event_id
    properties:
      source_id: string
      event_type: string
      event_time: timestamp
      observed_time: timestamp
      payload_hash: string
      confidence: float
      classification: string
      release_marks: string[]
      raw_lineage_refs: string[]
      mission_ids: string[]

  Entity:
    key: entity_id
    properties:
      entity_type: enum[PERSON, ORGANIZATION, ASSET, ACCOUNT, DEVICE, LOCATION, INFRASTRUCTURE]
      display_name: string
      aliases: string[]
      confidence: float
      risk_score: float
      compartments: string[]
      source_lineage: string[]
      valid_from: timestamp
      valid_to: timestamp?

  Relationship:
    key: relationship_id
    properties:
      src_entity_id: string
      dst_entity_id: string
      relation_type: string
      confidence: float
      evidence_event_ids: string[]
      valid_from: timestamp
      valid_to: timestamp?
      asserted_by: enum[SOURCE, MODEL, OPERATOR, TRANSFORM]
      approval_status: enum[DRAFT, REVIEWED, REJECTED, VERIFIED]

  Alert:
    key: alert_id
    properties:
      mission_id: string
      severity: enum[INFO, LOW, MEDIUM, HIGH, CRITICAL]
      status: enum[NEW, TRIAGED, ENRICHED, CORRELATED, AWAITING_APPROVAL, APPROVED, REJECTED, CLOSED]
      reason_codes: string[]
      linked_event_ids: string[]
      linked_entity_ids: string[]
      recommended_action_id: string?
      model_version: string?
      prompt_version: string?
      workflow_version: string?
      operator_outcome: enum[TRUE_POSITIVE, FALSE_POSITIVE, DUPLICATE, STALE, ESCALATED]?

  AgentRun:
    key: run_id
    properties:
      mission_id: string
      operator_id: string
      agent_name: string
      prompt_version: string
      model_id: string
      workflow_version: string
      tools_used: string[]
      input_hash: string
      output_hash: string
      policy_decisions: object[]
      latency_ms: int
      created_at: timestamp

  FeedbackSignal:
    key: signal_id
    properties:
      mission_id: string
      actor_id: string
      target_type: enum[ALERT, ENTITY, RELATIONSHIP, AGENT_RUN, INTEL_PRODUCT, RECOMMENDATION]
      target_id: string
      rating: int
      correction: string?
      disposition: enum[HELPFUL, PARTIAL, WRONG, UNSAFE, DUPLICATE]
      outcome_label: string?
      captured_at: timestamp

  ChangeProposal:
    key: proposal_id
    properties:
      change_type: enum[PROMPT, WORKFLOW, MODEL_ROUTE, HEURISTIC, POLICY]
      target_artifact: string
      proposed_diff_uri: string
      eval_report_uri: string
      risk_score: float
      blast_radius: string
      rollback_target: string
      approval_status: enum[DRAFT, IN_REVIEW, APPROVED, REJECTED, DEPLOYED, ROLLED_BACK]
```

### Relationship graph

```yaml
Relationships:
  ENTITY_OBSERVED_IN_EVENT: Entity -> IntelEvent
  ENTITY_ASSOCIATED_WITH_ENTITY: Entity -> Entity
  ALERT_DERIVED_FROM_EVENT: Alert -> IntelEvent
  ALERT_SUPPORTS_MISSION: Alert -> Mission
  CASE_CONTAINS_ALERT: Case -> Alert
  AGENT_RUN_PRODUCED_ALERT: AgentRun -> Alert
  FEEDBACK_EVALUATES_AGENT_RUN: FeedbackSignal -> AgentRun
  FEEDBACK_EVALUATES_ALERT: FeedbackSignal -> Alert
  CHANGE_PROPOSAL_MODIFIES_ARTIFACT: ChangeProposal -> PromptVersion|WorkflowVersion|ModelRouteVersion|PolicyBundleVersion
```

### Ontology invariants

- Every object and relationship carries classification, compartments, release marks, lineage, confidence, valid time, and system time.
- Every AI input is derived from a policy-filtered object set.
- Every AI output is stored as a draft until an ontology action, policy decision, or human approval promotes it.
- Temporal truth is explicit: `valid_time` represents domain truth, while `system_time` represents when Artemis believed or changed the assertion.
- Coalition sharing requires explicit release marks and release authority; role membership alone never grants cross-boundary access.

## AI and Agent Design

### Copilots

| Copilot | Users | Capabilities | Hard limits |
| --- | --- | --- | --- |
| Analyst Copilot | Analysts and investigators | Explain alerts, summarize timelines, draft RFIs, identify evidence gaps, generate cited notes | Cannot close cases, fabricate uncited claims, or broaden access |
| Commander Copilot | Commanders and mission leads | Mission posture, risk briefs, courses of action, resource impact, confidence caveats | Cannot execute operational response without approval |
| Data Steward Copilot | Data owners | Schema drift, lineage gaps, entity resolution issues, source reliability | Cannot alter ontology mappings without review |
| Eval Steward Copilot | Governance reviewers | Prompt diffs, workflow diffs, eval deltas, regression summaries | Cannot deploy changes directly |

### Multi-agent workflow

```text
IntelEvent
  -> Triage Agent
  -> Enrichment Agent
  -> Correlation Agent
  -> Summarization Agent
  -> Recommendation Agent
  -> Human Approval Gate
  -> Gotham Case / Foundry Action / Intel Product
```

| Agent | Tools | Output | Approval gate |
| --- | --- | --- | --- |
| Triage | ontology lookup, dedupe, severity classifier | alert draft and reason codes | Low-risk draft creation may be automatic |
| Enrichment | sanctioned APIs, internal search, graph expansion | enriched profile and evidence bundle | Required for sensitive or external paid queries |
| Correlation | graph query, temporal joins, vector retrieval | hypotheses and relationship proposals | Required for high-impact assertions |
| Summarization | citation compiler, redaction, product template | sourced intel product draft | Always human review |
| Recommendation | action templates, risk scoring, policy simulation | action package | Always human approval |
| Improvement | eval runner, diff generator, shadow replay | change proposal | Governance approval + Apollo canary |

### Tool execution envelope

```json
{
  "run_id": "arun_01JARTEMIS",
  "mission_id": "mis_artemis_northstar",
  "operator_id": "usr_analyst_17",
  "tool": "ontology.query",
  "purpose": "alert_triage",
  "classification": "SECRET//REL-USA-CAN",
  "arguments_hash": "sha256:...",
  "policy_token": "opaque-short-lived-token",
  "expires_at": "2026-07-20T18:30:00Z"
}
```

## Self-Improvement Loop

Artemis improves itself by proposing changes to prompts, workflows, heuristics, and model routing. It never silently changes operational authority, mission objectives, approval gates, policy boundaries, or external action permissions.

### Signal-to-upgrade pipeline

1. **Capture** operator corrections, accepted/rejected recommendations, query logs, alert outcomes, mission results, latency, policy denials, citation defects, and trust ratings.
2. **Normalize** signals into typed `FeedbackSignal` records with redaction, lineage, mission scope, and target artifact references.
3. **Generate eval cases** containing input context, expected output, policy constraints, labels, and known failure modes.
4. **Run frozen regression suites** against current and candidate prompt/workflow/router versions.
5. **Generate proposal** with diff, rationale, eval deltas, known risks, policy impact, blast radius, and rollback target.
6. **Review** by mission owner, security owner, model governance owner, and data owner where applicable.
7. **Canary** through Apollo to a limited cohort without reducing approval requirements.
8. **Monitor** precision, recall, unsupported-claim rate, operator override rate, p95 latency, policy denial spikes, and data/model drift.
9. **Promote or rollback** automatically based on signed health gates and immutable release evidence.

### Metrics

```yaml
quality_metrics:
  precision_min: 0.91
  recall_min: 0.86
  citation_coverage_min: 0.98
  unsupported_claim_rate_max: 0.01
  false_positive_rate_delta_max: 0.00
  operator_override_rate_delta_max: 0.03
latency_metrics:
  triage_p95_ms_max: 750
  recommendation_p95_ms_max: 1800
trust_metrics:
  trust_rating_min: 4.1
  rejection_rate_delta_max: 0.02
safety_metrics:
  policy_violations_max: 0
  cross_coalition_leakage_max: 0
  approval_gate_bypass_max: 0
```

## Full-Stack Implementation

### Frontend blueprint

- Mission overview with live event stream, risk posture, open cases, and SLO health.
- Analyst case workbench with evidence timeline, entity graph, chat-based copilot, citations, and approval widgets.
- Commander dashboard with courses of action, confidence bands, blast radius, and required approvals.
- Governance console with prompt/workflow diffs, eval reports, shadow-mode results, release history, and rollback controls.
- Audit console with who/what/when/why, source lineage, tool calls, model versions, policy decisions, and output hashes.

### Backend and data blueprint

- **API gateway/BFF**: validates OIDC/JWT, injects mission context, calls policy decision point, redacts responses.
- **Alert service**: consumes normalized events, deduplicates alerts, manages state transitions and reason codes.
- **Case service**: synchronizes Gotham cases, ownership, evidence bundles, and review status.
- **Ontology service**: exposes mission-scoped reads and guarded actions backed by Foundry object sets.
- **Agent orchestrator**: runs AIP workflows, signs tool envelopes, enforces tool policies, records `AgentRun` objects.
- **Feedback service**: stores corrections/outcomes and emits eval-generation events.
- **Governance service**: manages `ChangeProposal` review, approval, release gating, and evidence packs.
- **Model router**: selects approved models by task, classification, latency SLO, risk, and eval performance.

## Security and Governance

- **Need-to-know access control**: ABAC with mission assignment, clearance, compartments, coalition membership, device posture, location, purpose, and time.
- **Fine-grained permissions**: row-, column-, entity-, relationship-, and property-level controls before UI or AI access.
- **Compartmentalization**: strict partitioning by classification and coalition release markings; explicit downgrading/release workflow only.
- **Zero-trust execution**: mTLS, workload identity, short-lived credentials, signed tool tokens, network policy, and default-deny egress.
- **Immutable provenance**: append-only audit records for source ingestion, transforms, model calls, tool calls, approvals, denials, deployments, and rollbacks.
- **Prompt/model governance**: versioned artifacts, owners, diffs, eval reports, known limitations, retirement dates, and signed approvals.
- **Policy-as-code**: Rego/Cedar bundles tested in CI, released through Apollo, and pinned by version in every runtime decision.
- **Secret handling**: secrets remain in managed vaults, never appear in prompts, logs, model context, eval fixtures, PRs, or error messages.

## Code Examples

### Python backend feedback service

```python
from datetime import datetime, timezone
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="ClearGlassInc Artemis Feedback API")

class AuthContext(BaseModel):
    user_id: str
    missions: set[str]
    compartments: set[str]
    release_marks: set[str]
    roles: set[str]

class FeedbackIn(BaseModel):
    mission_id: str
    target_id: str
    target_type: Literal["alert", "agent_run", "intel_product", "entity_link"]
    signal_type: Literal["rating", "correction", "rejection", "approval", "outcome"]
    rating: int | None = Field(default=None, ge=1, le=5)
    correction: str | None = Field(default=None, max_length=4000)
    outcome_label: str | None = Field(default=None, max_length=80)

async def current_auth() -> AuthContext:
    return AuthContext(
        user_id="usr_demo",
        missions={"mis_artemis_northstar"},
        compartments={"ARTEMIS", "MUNICIPAL-CYBER"},
        release_marks={"REL-USA-CAN"},
        roles={"analyst"},
    )

async def publish(topic: str, event: dict) -> None:
    # Production: publish to Kafka/Pulsar with schema validation and delivery guarantees.
    return None

async def append_audit(event_type: str, actor: str, payload_hash: str) -> None:
    # Production: append to immutable audit log with WORM retention.
    return None

@app.post("/feedback")
async def record_feedback(payload: FeedbackIn, auth: AuthContext = Depends(current_auth)) -> dict:
    if payload.mission_id not in auth.missions:
        raise HTTPException(status_code=403, detail="mission access denied")

    event = {
        "signal_id": "sig_generated_by_ulid",
        "mission_id": payload.mission_id,
        "target_id": payload.target_id,
        "target_type": payload.target_type,
        "signal_type": payload.signal_type,
        "rating": payload.rating,
        "correction": payload.correction,
        "outcome_label": payload.outcome_label,
        "created_by": auth.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await publish("feedback.recorded", event)
    await append_audit("feedback.recorded", auth.user_id, payload_hash="sha256:redacted")
    return event
```

### Python workflow state machine

```python
from enum import StrEnum
from pydantic import BaseModel

class AlertState(StrEnum):
    NEW = "new"
    TRIAGED = "triaged"
    ENRICHED = "enriched"
    CORRELATED = "correlated"
    RECOMMENDED = "recommended"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"

class Transition(BaseModel):
    source: AlertState
    target: AlertState
    requires_human_approval: bool = False

TRANSITIONS = {
    (AlertState.NEW, AlertState.TRIAGED): Transition(source=AlertState.NEW, target=AlertState.TRIAGED),
    (AlertState.TRIAGED, AlertState.ENRICHED): Transition(source=AlertState.TRIAGED, target=AlertState.ENRICHED),
    (AlertState.ENRICHED, AlertState.CORRELATED): Transition(source=AlertState.ENRICHED, target=AlertState.CORRELATED),
    (AlertState.CORRELATED, AlertState.RECOMMENDED): Transition(source=AlertState.CORRELATED, target=AlertState.RECOMMENDED),
    (AlertState.RECOMMENDED, AlertState.AWAITING_APPROVAL): Transition(
        source=AlertState.RECOMMENDED,
        target=AlertState.AWAITING_APPROVAL,
        requires_human_approval=True,
    ),
}

def next_state(current: AlertState, target: AlertState, human_approved: bool) -> AlertState:
    transition = TRANSITIONS.get((current, target))
    if transition is None:
        raise ValueError(f"invalid transition: {current} -> {target}")
    if transition.requires_human_approval and not human_approved:
        raise PermissionError("human approval required")
    return transition.target
```

### Ontology-driven mission query

```sql
SELECT
  e.entity_id,
  e.entity_type,
  e.display_name,
  r.relation_type,
  r.confidence,
  r.valid_from,
  r.valid_to,
  l.source_dataset,
  l.transform_id
FROM ontology_entities e
JOIN ontology_relationships r ON r.dst_entity_id = e.entity_id
JOIN ontology_lineage l ON l.object_id = r.relationship_id
JOIN mission_entity_acl acl ON acl.entity_id = e.entity_id
WHERE r.src_entity_id = :seed_entity_id
  AND acl.mission_id = :mission_id
  AND acl.principal_id = :operator_id
  AND e.classification_rank <= :principal_clearance_rank
  AND r.confidence >= 0.72
  AND tstzrange(r.valid_from, COALESCE(r.valid_to, 'infinity')) @> NOW()
ORDER BY r.confidence DESC, r.valid_from DESC
LIMIT 100;
```

### AIP-style tool call

```python
from pydantic import BaseModel

class ToolContext(BaseModel):
    run_id: str
    principal_id: str
    mission_id: str
    prompt_version: str
    model_version: str
    workflow_version: str
    policy_token: str

class OpenCaseArgs(BaseModel):
    title: str
    alert_ids: list[str]
    summary: str
    requested_severity: str

async def open_case_tool(ctx: ToolContext, args: OpenCaseArgs) -> dict:
    await audit_log("tool.requested", {"run_id": ctx.run_id, "tool": "case.open"})
    await check_policy_for_tool(ctx, "case.open", args.model_dump())
    case_id = await create_gotham_case(
        mission_id=ctx.mission_id,
        title=args.title,
        alert_ids=args.alert_ids,
        summary=args.summary,
        severity=args.requested_severity,
    )
    await audit_log("tool.completed", {"run_id": ctx.run_id, "case_id": case_id})
    return {"case_id": case_id, "status": "opened"}
```

### Policy-as-code

```rego
package artemis.authz

default allow := false

allow if {
  input.action == "ontology.read"
  input.resource.mission_id in input.principal.missions
  input.resource.classification_rank <= input.principal.clearance_rank
  every compartment in input.resource.compartments { compartment in input.principal.compartments }
  every mark in input.resource.release_marks { mark in input.principal.release_marks }
}

requires_human_approval if {
  input.action in {
    "recommend_operational_response",
    "release_intel_product",
    "share_cross_coalition",
    "deploy_prompt_version",
    "deploy_workflow_version"
  }
}

deny_reason := "cross-coalition release requires explicit release authority" if {
  input.action == "share_cross_coalition"
  not input.principal.release_authority
}
```

### Eval pipeline

```python
from statistics import mean
from pydantic import BaseModel

class EvalCase(BaseModel):
    case_id: str
    input_context: dict
    expected_label: str
    policy_constraints: list[str]

class EvalResult(BaseModel):
    case_id: str
    predicted_label: str
    latency_ms: int
    unsupported_claims: int
    policy_violations: list[str]

async def run_eval_suite(candidate_prompt: str, cases: list[EvalCase]) -> dict:
    results: list[EvalResult] = []
    for case in cases:
        raw = await call_shadow_agent(prompt=candidate_prompt, context=case.input_context)
        results.append(EvalResult(**raw))

    correct = [r.predicted_label == c.expected_label for r, c in zip(results, cases)]
    latencies = sorted(r.latency_ms for r in results)
    report = {
        "accuracy": mean(correct),
        "p95_latency_ms": latencies[max(0, int(len(latencies) * 0.95) - 1)],
        "unsupported_claims": sum(r.unsupported_claims for r in results),
        "policy_violations": sum(len(r.policy_violations) for r in results),
    }
    report["passed"] = (
        report["accuracy"] >= 0.91
        and report["p95_latency_ms"] <= 1800
        and report["unsupported_claims"] == 0
        and report["policy_violations"] == 0
    )
    await persist_eval_report(report, [r.model_dump() for r in results])
    return report
```

### TypeScript model router

```typescript
type Classification = "UNCLASSIFIED" | "PROTECTED" | "SECRET" | "TOP_SECRET";
type Task = "triage" | "enrich" | "correlate" | "summarize" | "recommend";

type RouteRequest = {
  missionId: string;
  task: Task;
  classification: Classification;
  risk: "low" | "medium" | "high";
  maxLatencyMs: number;
};

export function selectModel(req: RouteRequest): string {
  if (req.classification === "TOP_SECRET") return "airgapped-sovereign-reasoner-v1";
  if (req.classification === "SECRET") return "sovereign-secure-llm-v3";
  if (req.task === "recommend" || req.risk === "high") return "deep-reasoning-governed-v4";
  if (req.maxLatencyMs < 750) return "small-fast-triage-model-v2";
  return "balanced-intel-model-v3";
}
```

### Apollo release gate

```yaml
release:
  name: artemis-agent-orchestrator
  artifact: registry.clearglassinc.local/artemis/agent-orchestrator:2.4.0
  signed: true
  sbom_required: true
  environments: [dev, staging, mission-canary, production]
  gates:
    - unit_tests_passed
    - policy_tests_passed
    - eval_accuracy_gte_0_91
    - unsupported_claim_rate_lte_0_01
    - policy_violations_eq_0
    - p95_latency_lte_1800ms
    - human_approvals:
        required: [mission_owner, security_owner, model_governance_owner]
  canary:
    initial_percent: 5
    max_percent_without_manual_promotion: 25
  rollback:
    automatic_on:
      - policy_violation_spike
      - p95_latency_breach_10m
      - operator_rejection_rate_regression
      - eval_shadow_regression
```

## Scenario Walkthrough

At 09:14 UTC, a live intelligence event enters `intel.raw` from a sanctioned telemetry source. Foundry validates the schema, hashes the raw artifact, assigns classification and release markings, deduplicates the event, and emits a normalized record to `intel.normalized`. The ontology materializer links the event to a municipal asset, a contractor account, and two historical intrusion clusters with confidence scores and evidence IDs.

The AIP Triage Agent receives a least-privilege task envelope. It queries only mission-authorized objects, detects overlap with a vulnerable service, and creates a `HIGH` severity alert draft with reason codes and citations. The Enrichment Agent requests additional internal context. Policy allows internal graph expansion but denies one external enrichment call because the release markings do not authorize that coalition boundary.

The Correlation Agent finds a matching maintenance-window record and lowers one hypothesis from high confidence to medium confidence. The Recommendation Agent drafts an action package: preserve logs, isolate the contractor account after commander approval, notify municipal IT, and open a Gotham case. Because the package has operational impact, Artemis moves it to `AWAITING_APPROVAL`.

The analyst approves opening the Gotham case and preserving logs, edits the summary wording, and rejects immediate account isolation because the maintenance window suggests legitimate activity. The feedback service records the edit, rejection reason, maintenance-window evidence, final alert disposition, and trust rating.

Overnight, the Improvement Agent converts this outcome into an eval case. It proposes a workflow update requiring a maintenance-window lookup before account-isolation recommendations. The eval suite reduces false positives without reducing recall, shadow mode shows no policy violations, and governance reviewers approve a 5% canary. Apollo deploys the signed workflow version, monitors latency, override rate, and policy denials, then promotes it. If any health gate regresses, Apollo automatically rolls back to the prior signed workflow and preserves the failed proposal for audit.

## Remaining risks and follow-up work

- Integrate this blueprint with concrete Foundry object/action definitions when environment-specific ontology names are known.
- Replace illustrative model identifiers with the organization-approved AIP model catalog.
- Map real coalition release markings, classification labels, and approval matrices to policy-as-code tests.
- Build runnable service stubs only after repository service boundaries and deployment targets are confirmed.
