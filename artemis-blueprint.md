# ClearGlassInc Artemis — Self-Evolving AI Intelligence Platform Blueprint

ClearGlassInc Artemis is a secure, coalition-aware, latency-sensitive intelligence platform blueprint built around Palantir Gotham, Foundry, AIP, and Apollo. It is designed for audited mission operations where AI agents accelerate triage, enrichment, correlation, summarization, and recommendation while humans retain approval authority for operationally significant actions.

## System Architecture

### Control-plane map

| Layer | Primary responsibility | Palantir anchor | Production components |
|---|---|---|---|
| Frontend | Analyst cockpit, commander overview, case workbench, eval review console | Gotham applications + Foundry apps | Next.js, React Server Components, MapLibre/Deck.gl, WebSocket/SSE streams |
| API gateway | Request normalization, auth context, rate limits, audit envelope | Foundry application logic | Envoy/Kong, OpenAPI, OPA sidecar, signed request IDs |
| Backend services | Case management, alert triage, entity enrichment, action package generation | Gotham operations + Foundry services | Python FastAPI, Temporal, Celery/RQ, Redis, Postgres |
| Data layer | Live and historical ingestion, lakehouse, transforms, search | Foundry pipelines + ontology | Foundry datasets, Iceberg/Delta, Kafka/Redpanda, OpenSearch, pgvector |
| Ontology layer | Typed operational entities, links, permissions, lineage, temporal state | Foundry Ontology + Gotham entity model | Entity schemas, relationship schemas, confidence scoring, provenance graph |
| AI orchestration | Copilots, agents, tools, evals, prompt/model routing | AIP | LangGraph/Temporal workflows, model router, tool registry, eval harness |
| Policy layer | Need-to-know, coalition boundaries, approval gates, model constraints | Foundry security + AIP guardrails | OPA/Rego, Cedar-style ABAC, policy-as-code, signed approvals |
| Observability | Metrics, traces, immutable audit logs, eval dashboards | Foundry telemetry + Apollo runtime | OpenTelemetry, Prometheus, Grafana, SIEM export, append-only object store |
| Deployment | Secure releases, progressive rollout, rollback, runtime controls | Apollo | GitHub Actions, container signing, SBOM, SLSA provenance, canaries |

### Request lifecycle

1. A live source emits an event to the streaming bus.
2. Foundry pipelines validate, deduplicate, classify, and attach lineage.
3. The ontology service maps the event to entities, relationships, confidence scores, and mission context.
4. AIP agents receive a policy-filtered task envelope with only authorized data views.
5. Agents run triage, enrichment, correlation, and recommendation workflows through registered tools.
6. The backend opens or updates a Gotham case and prepares an action package.
7. Operators approve, edit, reject, or escalate the package.
8. Feedback, outcomes, and latency/quality metrics become eval data for safe improvement proposals.
9. Apollo deploys approved prompt, workflow, policy, or model-routing changes with canary controls and rollback.

## Data and Ontology

### Core ontology entities

| Entity | Purpose | Critical attributes |
|---|---|---|
| `Mission` | Operational objective and rules of engagement | `mission_id`, `classification`, `coalition_scope`, `objectives`, `approval_matrix` |
| `IntelEvent` | Raw or normalized incoming signal | `event_id`, `source_id`, `timestamp`, `payload_hash`, `confidence`, `classification` |
| `Entity` | Person, organization, infrastructure, asset, account, location, or device | `entity_id`, `entity_type`, `aliases`, `risk_score`, `compartments` |
| `Relationship` | Temporal edge between entities | `src`, `dst`, `relation_type`, `valid_from`, `valid_to`, `confidence`, `evidence_ids` |
| `Case` | Investigation container | `case_id`, `mission_id`, `status`, `priority`, `assignees`, `linked_entities` |
| `Alert` | Triage object requiring review | `alert_id`, `severity`, `reason_codes`, `dedupe_key`, `recommended_action` |
| `IntelProduct` | Human-readable output | `product_id`, `format`, `citations`, `classification`, `review_status` |
| `AgentRun` | AI execution record | `run_id`, `prompt_version`, `model_id`, `tools_used`, `policy_decisions`, `outputs` |
| `FeedbackSignal` | Operator and outcome learning data | `signal_id`, `signal_type`, `target_id`, `rating`, `correction`, `mission_outcome` |
| `ChangeProposal` | Self-improvement candidate | `proposal_id`, `change_type`, `diff`, `eval_delta`, `risk_score`, `approval_status` |

### Relationship examples

- `Entity OBSERVED_IN IntelEvent` with evidence lineage.
- `Entity ASSOCIATED_WITH Entity` with temporal validity and confidence.
- `Alert GENERATED_FROM IntelEvent` for auditability.
- `Case CONTAINS Alert` for analyst workflows.
- `AgentRun PRODUCED IntelProduct` for model governance.
- `FeedbackSignal EVALUATES AgentRun` for continuous improvement.
- `ChangeProposal MODIFIES PromptVersion|WorkflowVersion|RoutingPolicy` for controlled upgrades.

### Ontology rules

- Every assertion must carry `confidence`, `lineage`, `valid_time`, `ingest_time`, and `classification`.
- Every query is mission-scoped and policy-filtered before retrieval.
- AI agents never receive raw unrestricted ontology access; they receive a least-privilege tool token and a mission-bounded view.
- Temporal state is first-class: historical truth, current belief, and projected risk are distinct.
- Coalition sharing uses explicit release markings rather than implicit role membership.

## AI and Agent Design

### Copilots

- **Analyst Copilot:** explains alerts, summarizes entity timelines, drafts RFIs, and asks for missing evidence.
- **Commander Copilot:** provides mission-level risk posture, decision briefs, resource impacts, and confidence caveats.
- **Data Steward Copilot:** flags lineage gaps, schema drift, stale sources, and ontology quality issues.
- **Eval Steward Copilot:** reviews proposed prompt/workflow changes and summarizes regression risks.

### Multi-agent workflows

| Agent | Inputs | Tools | Outputs | Approval gate |
|---|---|---|---|---|
| Triage Agent | `IntelEvent`, mission context | ontology lookup, dedupe, severity model | `Alert` and reason codes | No for low-risk alert creation |
| Enrichment Agent | Alert entities | sanctioned APIs, search, graph expansion | enriched entity profile | Yes for external paid or sensitive queries |
| Correlation Agent | Entity graph neighborhood | graph query, vector retrieval, temporal join | likely relationships and hypotheses | Yes for high-impact assertions |
| Summarization Agent | case evidence bundle | citation compiler, redaction tool | intel product draft | Human review required |
| Recommendation Agent | case state, policy, objectives | action templates, risk model | action package | Human approval required |
| Improvement Agent | feedback/eval data | eval runner, diff generator | change proposal | Human approval + canary required |

### Tool contract

Every AI tool call uses a signed execution envelope:

```json
{
  "run_id": "arun_01J...",
  "mission_id": "mis_artemis_northstar",
  "operator_id": "usr_analyst_17",
  "tool": "ontology.query",
  "purpose": "alert_triage",
  "classification": "SECRET//REL-CAN-USA",
  "arguments_hash": "sha256:...",
  "policy_token": "opaque-short-lived-token",
  "expires_at": "2026-06-29T18:30:00Z"
}
```

## Self-Improvement Loop

### Signals captured

- Operator corrections to entity resolution, summaries, alert severity, and recommended actions.
- Query logs, tool latency, empty-result rates, and policy denials.
- Alert outcomes such as true positive, false positive, duplicate, stale, or escalated.
- Mission results including time-to-triage, time-to-brief, decision quality, and trust rating.
- Model behavior metrics: hallucination flags, citation coverage, unsupported claim rate, and refusal quality.

### Safe improvement pipeline

1. **Capture:** event-sourced feedback is written to immutable storage and normalized into `FeedbackSignal`.
2. **Label:** sensitive text is redacted; labels are assigned for precision, recall, latency, trust, and impact.
3. **Evaluate:** candidate prompts, workflows, and routers run against frozen eval suites and adversarial tests.
4. **Propose:** the Improvement Agent creates a `ChangeProposal` with diffs, metrics, blast radius, and rollback plan.
5. **Review:** human approvers inspect evidence, eval deltas, and policy impact.
6. **Canary:** Apollo deploys the approved version to a limited mission cohort.
7. **Monitor:** drift, regressions, operator overrides, and policy denials are watched in real time.
8. **Promote or rollback:** successful canaries are promoted; regressions trigger automatic rollback to the last signed version.

### Guardrails

- The system can propose improvements but cannot autonomously change mission objectives, approval gates, policy boundaries, or external action authority.
- Prompt/workflow/model changes are versioned, signed, evaluated, approved, and deployed as immutable artifacts.
- A/B tests are mission-safe: no test variant can reduce required human approval or access broader data.
- Drift detection compares current distributions to baseline mission windows for source quality, embeddings, labels, and outcomes.

## Full-Stack Implementation

### Frontend

- Next.js cockpit with server-rendered mission overview, streaming alert panels, entity graph views, and eval review queues.
- Role-aware layouts: analyst, commander, steward, auditor.
- Every AI answer displays citations, confidence, source classification, tool history, and review status.

### Backend

- FastAPI services for alerts, cases, ontology reads, feedback capture, and change proposals.
- Temporal workflows for long-running enrichment, review, and canary promotion.
- Postgres for transactional state; Foundry datasets/lakehouse for analytical and historical state.
- Kafka/Redpanda topics for `intel.raw`, `intel.normalized`, `alerts.created`, `feedback.recorded`, and `proposals.created`.

### Retrieval and inference

- OpenSearch for lexical search over reports and cases.
- pgvector or a governed vector index for embeddings with classification-aware partitioning.
- Model router chooses small, fast, local, or frontier models based on task sensitivity, latency SLO, classification, and eval history.

## Security and Governance

- Zero-trust request validation with mTLS, workload identity, signed JWTs, and short-lived tool tokens.
- ABAC/RBAC/ReBAC policy: user role, mission assignment, entity compartments, coalition release marks, action type, and purpose.
- Row-, column-, entity-, and edge-level controls are enforced before data reaches agents or UI components.
- Immutable audit logs include who/what/when/why, prompt version, model ID, tool args hash, policy result, and output hash.
- Model governance tracks model cards, approved data domains, eval results, known limitations, and retirement dates.
- Prompt governance stores owners, versions, diffs, approvals, eval deltas, deployment rings, and rollback targets.

## Code Examples

### Python FastAPI feedback endpoint

```python
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends

app = FastAPI(title="ClearGlassInc Artemis Feedback API")

class AuthContext(BaseModel):
    user_id: str
    mission_ids: set[str]
    compartments: set[str]
    roles: set[str]

class FeedbackIn(BaseModel):
    target_id: str
    target_type: str = Field(pattern="^(alert|agent_run|intel_product|entity_link)$")
    signal_type: str
    rating: int = Field(ge=1, le=5)
    correction: str | None = None
    mission_id: str

def current_auth() -> AuthContext:
    return AuthContext(user_id="usr_demo", mission_ids={"mis_artemis"}, compartments={"REL-CAN"}, roles={"analyst"})

def assert_mission_access(auth: AuthContext, mission_id: str) -> None:
    if mission_id not in auth.mission_ids:
        raise PermissionError("mission access denied")

@app.post("/feedback")
def record_feedback(payload: FeedbackIn, auth: AuthContext = Depends(current_auth)):
    assert_mission_access(auth, payload.mission_id)
    feedback = {
        "signal_id": "sig_generated",
        "mission_id": payload.mission_id,
        "target_id": payload.target_id,
        "signal_type": payload.signal_type,
        "rating": payload.rating,
        "correction": payload.correction,
        "created_by": auth.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    # publish("feedback.recorded", feedback)
    # append_audit("feedback.recorded", auth, feedback)
    return feedback
```

### Policy-as-code sketch

```rego
package artemis.authz

default allow := false

allow if {
  input.purpose in {"alert_triage", "case_review", "intel_product_draft"}
  input.user.missions[_] == input.resource.mission_id
  every mark in input.resource.release_marks { mark in input.user.release_marks }
  not input.action in {"external_tasking", "public_release"}
}

requires_human_approval if {
  input.action in {"recommend_operational_response", "open_external_case", "release_intel_product"}
}
```

### Ontology-driven SQL query

```sql
SELECT e.entity_id, e.entity_type, e.display_name, r.relation_type, r.confidence, r.valid_from, r.valid_to
FROM ontology_entities e
JOIN ontology_relationships r ON r.dst_entity_id = e.entity_id
JOIN mission_entity_acl acl ON acl.entity_id = e.entity_id
WHERE r.src_entity_id = :seed_entity_id
  AND acl.mission_id = :mission_id
  AND acl.principal_id = :operator_id
  AND r.confidence >= 0.72
  AND tstzrange(r.valid_from, COALESCE(r.valid_to, 'infinity')) @> NOW()
ORDER BY r.confidence DESC, r.valid_from DESC
LIMIT 100;
```

### Workflow state machine

```python
from enum import StrEnum
from pydantic import BaseModel

class AlertState(StrEnum):
    RECEIVED = "received"
    TRIAGED = "triaged"
    ENRICHED = "enriched"
    CORRELATED = "correlated"
    PACKAGE_DRAFTED = "package_drafted"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"

class Transition(BaseModel):
    from_state: AlertState
    to_state: AlertState
    requires_approval: bool

TRANSITIONS = {
    (AlertState.RECEIVED, AlertState.TRIAGED): Transition(from_state=AlertState.RECEIVED, to_state=AlertState.TRIAGED, requires_approval=False),
    (AlertState.CORRELATED, AlertState.PACKAGE_DRAFTED): Transition(from_state=AlertState.CORRELATED, to_state=AlertState.PACKAGE_DRAFTED, requires_approval=False),
    (AlertState.PACKAGE_DRAFTED, AlertState.AWAITING_APPROVAL): Transition(from_state=AlertState.PACKAGE_DRAFTED, to_state=AlertState.AWAITING_APPROVAL, requires_approval=True),
}
```

### Model router

```python
def choose_model(task: str, classification: str, latency_ms: int, risk: str) -> str:
    if classification.startswith("SECRET"):
        return "approved-sovereign-llm"
    if risk == "high" or task in {"recommendation", "legal_summary"}:
        return "frontier-reviewed-model"
    if latency_ms < 750:
        return "small-fast-triage-model"
    return "balanced-reasoning-model"
```

### Eval record

```yaml
eval_suite: artemis-alert-triage-v12
mission_domain: municipal-cyber-osint
metrics:
  precision_min: 0.91
  recall_min: 0.86
  p95_latency_ms_max: 1800
  unsupported_claim_rate_max: 0.01
  citation_coverage_min: 0.98
promotion_rules:
  require_human_approval: true
  canary_percentage: 5
  automatic_rollback_on_regression: true
```

## Scenario Walkthrough

At 09:14 UTC, a live cyber indicator enters `intel.raw` from a sanctioned collection source. Foundry validates the payload, checks schema compatibility, hashes the source artifact, and publishes `intel.normalized`. The ontology service links the indicator to a municipal asset, a known infrastructure vendor, and two historical phishing clusters with confidence scores and evidence IDs.

The Triage Agent receives a least-privilege task envelope. It queries only mission-authorized entities, deduplicates against recent alerts, and creates a medium-high severity alert because the indicator overlaps a vulnerable service and a recent credential-harvesting pattern. The Enrichment Agent requests additional context; policy allows internal enrichment but denies one external query because coalition release markings do not permit it. The Correlation Agent produces two hypotheses with citations and caveats.

The Recommendation Agent drafts an action package: notify the assigned municipal security contact, rotate a specific integration credential, block the indicator at the gateway, and open a follow-up case. Because this is operationally significant, Artemis marks the package `AWAITING_APPROVAL`. The analyst edits one sentence, lowers confidence on one relationship, approves the credential rotation recommendation, and rejects the external notification until a second source confirms the event.

The feedback system records the edit, rejection reason, confidence correction, and final outcome. Overnight, the Improvement Agent discovers that similar alerts were overconfident when only one source was available. It proposes a prompt diff and workflow rule requiring explicit second-source language for that pattern. The eval suite shows lower unsupported-claim rate with no recall loss. A human eval steward approves a 5% canary. Apollo deploys the signed workflow version, monitors override rates and latency, then promotes it when metrics stay inside thresholds. If the canary regresses, Apollo rolls back to the previous workflow and preserves the failed proposal for audit.

## Enumeration Operations Module

ClearGlassInc Artemis can support field enumeration as a governed case-management and decision-support workflow, but it must not impersonate an enumerator, contact residents autonomously, scrape restricted government systems, or submit official census responses without an authorized human operator. The platform therefore automates prioritization, routing, evidence packaging, reminders, audit capture, and supervisor reporting while keeping every resident contact, interview, verification, and final case disposition under trained-human control.

### Human-controlled operating model

| Capability | Automated by Artemis | Human approval / execution |
|---|---|---|
| Case import | Parse assigned workload tables, validate fields, detect duplicates, classify status codes | Confirm import source and assignment authority |
| Prioritization | Rank by status, SSID sequence, location cluster, previous attempts, accessibility constraints, and time windows | Override route and priority when local knowledge requires it |
| Route planning | Build cluster-aware stop plans and estimated duration | Physically visit, phone, or otherwise contact respondents only through authorized channels |
| Interview support | Display scripts, required fields, policy reminders, and case history | Conduct the interview and record answers in approved systems |
| Completion verification | Queue 701 cases, show verification checklist, compare operator-entered metadata | Confirm completion status in the official system |
| Reporting | Generate daily progress, exceptions, unresolved cases, and audit summaries | Submit official reports through authorized channels |

### Enumeration case object

```yaml
EnumerationCase:
  case_number: string
  ssid: string
  normalized_ssid: integer
  survey: enum[CENSUS]
  activity: enum[I_E]
  address_label: string
  status_code: enum[429, 701]
  status_text: string
  cluster_key: string
  dwelling_type: enum[apartment, basement, residential_unit, unknown]
  priority_score: float
  assigned_operator_id: string
  contact_policy_id: string
  official_system_ref: string?
  audit:
    imported_at: timestamp
    imported_by: string
    source_hash: string
    route_version: string
```

### Deterministic prioritization

```python
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

class CaseStatus(StrEnum):
    FOLLOW_UP = "429"
    CLAIMS_COMPLETED = "701"

@dataclass(frozen=True)
class EnumerationCase:
    case_number: str
    ssid: str
    location: str
    status: CaseStatus
    survey: str = "CENSUS"
    activity: str = "I/E"

CLUSTER_ORDER = {
    "KING ST W": 0,
    "MARGARET ST": 1,
    "LOCKE ST S": 2,
    "STRATHCONA AVE S": 3,
    "MAIN ST W": 4,
    "NEW ST": 5,
}

STATUS_WEIGHT = {CaseStatus.FOLLOW_UP: 0, CaseStatus.CLAIMS_COMPLETED: 1}

def ssid_sequence(ssid: str) -> int:
    return int(ssid.split()[-1])

def cluster_key(location: str) -> str:
    for key in CLUSTER_ORDER:
        if key in location.upper():
            return key
    return "UNKNOWN"

def dwelling_type(location: str) -> str:
    normalized = location.upper()
    if "BSMT" in normalized:
        return "basement"
    if "-" in normalized or normalized[:1].isalpha():
        return "apartment"
    return "residential_unit"

def priority_tuple(case: EnumerationCase) -> tuple[int, int, int, str]:
    return (
        STATUS_WEIGHT[case.status],
        CLUSTER_ORDER.get(cluster_key(case.location), 99),
        ssid_sequence(case.ssid),
        case.case_number,
    )

def plan_workload(cases: Iterable[EnumerationCase]) -> list[EnumerationCase]:
    """Return a route-ready list without making contact or changing official records."""
    return sorted(cases, key=priority_tuple)
```

### Route plan output for the provided 24-case workload

| Stop | Cluster | Case | SSID | Location | Status | Operator action |
|---:|---|---|---|---|---|---|
| 1 | KING ST W | 86900420 | 35250617 0001 | 7-505 KING ST W | 429 | Attempt authorized follow-up |
| 2 | KING ST W | 78180922 | 35250617 0004 | 3-481 KING ST W | 429 | Attempt authorized follow-up |
| 3 | KING ST W | 86900790 | 35250617 0291 | 1A-595 KING ST W | 429 | Attempt authorized follow-up |
| 4 | KING ST W | 78181104 | 35250617 0296 | 202-595 KING ST W | 429 | Attempt authorized follow-up |
| 5 | KING ST W | 86900641 | 35250617 0301 | 302-595 KING ST W | 429 | Attempt authorized follow-up |
| 6 | KING ST W | 86900704 | 35250617 0313 | 504-595 KING ST W | 429 | Attempt authorized follow-up |
| 7 | MARGARET ST | 86900748 | 35250617 0070 | A-25 MARGARET ST | 429 | Attempt authorized follow-up |
| 8 | MARGARET ST | 78181186 | 35250617 0084 | 22-36 MARGARET ST | 429 | Attempt authorized follow-up |
| 9 | MARGARET ST | 86900635 | 35250617 0089 | 33-36 MARGARET ST | 429 | Attempt authorized follow-up |
| 10 | MARGARET ST | 86900764 | 35250617 0098 | 2-44 MARGARET ST | 429 | Attempt authorized follow-up |
| 11 | MARGARET ST | 78181240 | 35250617 0108 | 10-46 MARGARET ST | 429 | Attempt authorized follow-up |
| 12 | LOCKE ST S | 86900586 | 35250617 0014 | 2-24 LOCKE ST S | 429 | Attempt authorized follow-up |
| 13 | LOCKE ST S | 86900589 | 35250617 0015 | 3-24 LOCKE ST S | 429 | Attempt authorized follow-up |
| 14 | LOCKE ST S | 78181032 | 35250617 0024 | 42 LOCKE ST S | 429 | Attempt authorized follow-up |
| 15 | LOCKE ST S | 86900387 | 35250617 0030 | A-48 LOCKE ST S | 429 | Attempt authorized follow-up |
| 16 | STRATHCONA AVE S | 78181117 | 35250617 0208 | 2 STRATHCONA AVE S | 429 | Attempt authorized follow-up |
| 17 | STRATHCONA AVE S | 86900793 | 35250617 0215 | BSMT-10 STRATHCONA AVE S | 429 | Attempt authorized follow-up |
| 18 | STRATHCONA AVE S | 86900714 | 35250617 0238 | 4-46 STRATHCONA AVE S | 429 | Attempt authorized follow-up |
| 19 | STRATHCONA AVE S | 86900450 | 35250617 0241 | 2-50 STRATHCONA AVE S | 429 | Attempt authorized follow-up |
| 20 | MAIN ST W | 86900490 | 35250617 0039 | 352 MAIN ST W | 429 | Attempt authorized follow-up |
| 21 | MAIN ST W | 78181014 | 35250617 0040 | 354 MAIN ST W | 429 | Attempt authorized follow-up |
| 22 | NEW ST | 86900731 | 35250617 0289 | 19 NEW ST | 429 | Attempt authorized follow-up |
| 23 | STRATHCONA AVE S | 86900941 | 35250617 0229 | 2-38 STRATHCONA AVE S | 701 | Human verifies claimed completion |
| 24 | NEW ST | 86900726 | 35250617 0286 | 23 NEW ST | 701 | Human verifies claimed completion |

### Enumeration policy gates

```rego
package artemis.enumeration

default allow := false

authorized_case_read if {
  input.user.role in {"enumerator", "field_supervisor", "auditor"}
  input.case.assigned_operator_id == input.user.id
  input.case.survey == "CENSUS"
}

allow if {
  input.action == "plan_route"
  authorized_case_read
}

allow if {
  input.action == "record_attempt_notes"
  input.user.role == "enumerator"
  input.case.assigned_operator_id == input.user.id
  input.human_performed_contact == true
}

requires_human_action if {
  input.action in {"contact_resident", "conduct_interview", "verify_completion", "submit_official_status"}
}

deny_reason contains "AI may not autonomously contact residents or submit official census results" if {
  input.actor == "ai_agent"
  requires_human_action
}
```

### Backend API skeleton

```python
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/enumeration", tags=["enumeration"])

class AttemptNote(BaseModel):
    case_number: str
    outcome_code: str = Field(description="Operator-selected code from the authorized case system")
    notes: str = Field(max_length=2000)
    human_performed_contact: bool

class UserContext(BaseModel):
    user_id: str
    role: str
    assigned_case_numbers: set[str]

async def current_user() -> UserContext:
    return UserContext(user_id="usr_field_001", role="enumerator", assigned_case_numbers=set())

def require_case_assignment(user: UserContext, case_number: str) -> None:
    if user.role != "field_supervisor" and case_number not in user.assigned_case_numbers:
        raise HTTPException(status_code=403, detail="case is outside assigned workload")

@router.post("/attempts")
async def record_attempt(note: AttemptNote, user: UserContext = Depends(current_user)):
    require_case_assignment(user, note.case_number)
    if not note.human_performed_contact:
        raise HTTPException(status_code=400, detail="resident contact must be human-performed")
    event = {
        "event_type": "enumeration.attempt_recorded",
        "case_number": note.case_number,
        "outcome_code": note.outcome_code,
        "notes_hash": "sha256:redacted-at-rest",
        "recorded_by": user.user_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    # event_bus.publish("enumeration.attempts", event)
    # audit_log.append(event)
    return event
```

## Production Python Reference Skeleton

The implementation below makes the Artemis control loop concrete: typed events enter a bus, policy-filtered ontology reads ground the agent, workflow state is persisted, and every self-improvement proposal is evaluated before Apollo canary promotion.

### Repository layout

```text
services/
  artemis_api/
    app.py
    auth.py
    policy.py
    ontology.py
    agents.py
    workflows.py
    evals.py
    audit.py
  artemis_worker/
    consumers.py
    proposal_builder.py
web/
  app/mission/[missionId]/page.tsx
  components/ApprovalQueue.tsx
infra/
  opa/artemis.rego
  apollo/release.yaml
```

### Typed mission events

```python
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class Classification(StrEnum):
    UNCLASSIFIED = "UNCLASSIFIED"
    PROTECTED = "PROTECTED"
    SECRET_REL = "SECRET//REL-CAN-USA"
    TOP_SECRET = "TOP_SECRET"

class LineageRef(BaseModel):
    source_system: str
    source_uri: str
    artifact_hash: str
    ingested_at: datetime

class IntelEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    mission_id: str
    event_type: str
    event_time: datetime
    observed_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    classification: Classification
    compartments: set[str]
    release_marks: set[str]
    confidence: float = Field(ge=0, le=1)
    payload: dict[str, Any]
    lineage: list[LineageRef]

class AlertCreated(BaseModel):
    alert_id: str
    mission_id: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    reason_codes: list[str]
    evidence_event_ids: list[str]
    requires_human_review: bool = True
```

### Event consumer and triage handler

```python
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

async def consume_intel_events(bootstrap: str) -> None:
    consumer = AIOKafkaConsumer(
        "intel.normalized",
        bootstrap_servers=bootstrap,
        group_id="artemis-triage-v1",
        enable_auto_commit=False,
    )
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await consumer.start(); await producer.start()
    try:
        async for msg in consumer:
            event = IntelEvent.model_validate_json(msg.value)
            alert = await triage_event(event)
            await producer.send_and_wait(
                "alerts.created",
                AlertCreated(**alert).model_dump_json().encode(),
                key=event.mission_id.encode(),
            )
            await append_audit("triage.completed", subject="agent:triage", obj=alert)
            await consumer.commit()
    finally:
        await consumer.stop(); await producer.stop()

async def triage_event(event: IntelEvent) -> dict[str, object]:
    neighbors = await ontology_neighbors(
        mission_id=event.mission_id,
        seed_payload=event.payload,
        min_confidence=0.72,
    )
    severity = "HIGH" if any(n["risk_score"] > 0.85 for n in neighbors) else "MEDIUM"
    return {
        "alert_id": f"alt_{event.event_id}",
        "mission_id": event.mission_id,
        "severity": severity,
        "reason_codes": ["ontology_overlap", "live_source", "policy_review_required"],
        "evidence_event_ids": [event.event_id],
    }
```

### Policy-enforced ontology tool

```python
from dataclasses import dataclass
from opentelemetry import trace

tracer = trace.get_tracer("clearglassinc.artemis")

@dataclass(frozen=True)
class ToolContext:
    run_id: str
    operator_id: str
    mission_id: str
    purpose: str
    release_marks: frozenset[str]
    compartments: frozenset[str]

async def ontology_query_tool(ctx: ToolContext, cypher: str, params: dict[str, object]) -> list[dict[str, object]]:
    decision = await opa_decide(
        "data.artemis.authz.allow",
        {
            "action": "ontology.query",
            "purpose": ctx.purpose,
            "user": {"id": ctx.operator_id, "release_marks": list(ctx.release_marks)},
            "resource": {"mission_id": ctx.mission_id, "release_marks": list(ctx.release_marks)},
        },
    )
    if not decision["allow"]:
        await append_audit("tool.denied", subject=ctx.operator_id, obj={"run_id": ctx.run_id})
        raise PermissionError("ontology query denied by mission policy")

    with tracer.start_as_current_span("ontology.query") as span:
        span.set_attribute("mission_id", ctx.mission_id)
        span.set_attribute("run_id", ctx.run_id)
        rows = await foundry_ontology_client.query(cypher, params | {"mission_id": ctx.mission_id})
        redacted = redact_to_release_marks(rows, ctx.release_marks)
        await append_audit("tool.allowed", subject=ctx.operator_id, obj={"run_id": ctx.run_id, "rows": len(redacted)})
        return redacted
```

### Agent workflow graph

```python
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

class AgentState(BaseModel):
    mission_id: str
    alert_id: str
    evidence: list[dict] = []
    hypotheses: list[dict] = []
    recommendation: dict | None = None
    approval_status: str = "not_required"

async def enrich(state: AgentState) -> AgentState:
    state.evidence = await retrieve_evidence_bundle(state.mission_id, state.alert_id)
    return state

async def correlate(state: AgentState) -> AgentState:
    state.hypotheses = await run_correlation_model(state.evidence)
    return state

async def recommend(state: AgentState) -> AgentState:
    state.recommendation = await draft_action_package(state.evidence, state.hypotheses)
    state.approval_status = "awaiting_human"  # operationally significant by policy
    return state

workflow = StateGraph(AgentState)
workflow.add_node("enrich", enrich)
workflow.add_node("correlate", correlate)
workflow.add_node("recommend", recommend)
workflow.set_entry_point("enrich")
workflow.add_edge("enrich", "correlate")
workflow.add_edge("correlate", "recommend")
workflow.add_edge("recommend", END)
compiled_alert_workflow = workflow.compile()
```

### Evaluation and self-upgrade proposal pipeline

```python
from statistics import mean
from pydantic import BaseModel

class EvalCase(BaseModel):
    case_id: str
    input_bundle_uri: str
    expected_labels: set[str]
    minimum_citations: int

class EvalResult(BaseModel):
    suite: str
    candidate_version: str
    precision: float
    recall: float
    p95_latency_ms: int
    unsupported_claim_rate: float
    citation_coverage: float
    passed: bool

async def run_triage_eval(candidate_version: str, cases: list[EvalCase]) -> EvalResult:
    predictions: list[set[str]] = []
    latencies: list[int] = []
    citation_scores: list[float] = []
    unsupported = 0
    for case in cases:
        bundle = await load_eval_bundle(case.input_bundle_uri)
        output, latency_ms = await run_candidate_triage(candidate_version, bundle)
        predictions.append(set(output.labels))
        latencies.append(latency_ms)
        citation_scores.append(min(1.0, len(output.citations) / case.minimum_citations))
        unsupported += count_unsupported_claims(output)

    tp = sum(len(p & c.expected_labels) for p, c in zip(predictions, cases))
    fp = sum(len(p - c.expected_labels) for p, c in zip(predictions, cases))
    fn = sum(len(c.expected_labels - p) for p, c in zip(predictions, cases))
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    p95 = sorted(latencies)[int(len(latencies) * 0.95) - 1]
    result = EvalResult(
        suite="artemis-alert-triage-v12",
        candidate_version=candidate_version,
        precision=precision,
        recall=recall,
        p95_latency_ms=p95,
        unsupported_claim_rate=unsupported / max(len(cases), 1),
        citation_coverage=mean(citation_scores),
        passed=precision >= 0.91 and recall >= 0.86 and p95 <= 1800 and mean(citation_scores) >= 0.98,
    )
    await append_audit("eval.completed", subject="agent:improvement", obj=result.model_dump())
    return result

async def propose_upgrade(candidate_version: str, diff: str, eval_result: EvalResult) -> dict[str, object]:
    if not eval_result.passed:
        raise ValueError("candidate cannot be proposed because eval gates failed")
    proposal = {
        "proposal_id": f"chg_{candidate_version}",
        "change_type": "prompt_workflow_router",
        "candidate_version": candidate_version,
        "diff": diff,
        "eval_delta": eval_result.model_dump(),
        "approval_status": "awaiting_eval_steward",
        "apollo_canary": {"ring": "mission-canary", "percentage": 5, "rollback_on": ["precision_drop", "latency_regression", "policy_denial_spike"]},
    }
    await publish("proposals.created", proposal)
    return proposal
```

### Commander-facing API and UI contract

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/missions/{mission_id}")

@router.get("/situation")
async def situation_view(mission_id: str, auth: AuthContext = Depends(current_auth)):
    assert_mission_access(auth, mission_id)
    return {
        "mission_id": mission_id,
        "open_alerts": await count_open_alerts(mission_id, auth.user_id),
        "critical_entities": await top_risk_entities(mission_id, auth.user_id),
        "approval_queue": await pending_approvals(mission_id, auth.user_id),
        "model_health": await current_eval_health(mission_id),
    }
```

```tsx
export async function MissionSituation({ missionId }: { missionId: string }) {
  const res = await fetch(`/api/missions/${missionId}/situation`, { cache: "no-store" });
  const situation = await res.json();
  return (
    <section className="grid gap-4">
      <h1>ClearGlassInc Artemis Mission Situation</h1>
      <Metric label="Open Alerts" value={situation.open_alerts} />
      <ApprovalQueue items={situation.approval_queue} />
      <ModelHealthPanel health={situation.model_health} />
    </section>
  );
}
```

### Apollo release gate

```yaml
apiVersion: apollo.palantir.com/v1
kind: Release
metadata:
  name: artemis-agent-runtime
spec:
  artifact: registry.clearglass.example/artemis-agent-runtime:2.7.14
  signatures:
    required: true
    sbom: required
  rings:
    - name: dev-secure
      percent: 100
    - name: mission-canary
      percent: 5
      healthGates:
        - metric: eval_precision
          operator: ">="
          value: 0.91
        - metric: p95_latency_ms
          operator: "<="
          value: 1800
        - metric: policy_denial_spike
          operator: "=="
          value: false
    - name: mission-prod
      percent: 100
  rollback:
    automatic: true
    target: previous-signed
```

## Python Precision Implementation Blueprint

This section turns the architecture into a Python-first control surface for ClearGlassInc Artemis. The goal is deterministic behavior around security-sensitive boundaries: typed mission envelopes, explicit policy decisions, reproducible evaluations, and auditable self-improvement proposals.

### Typed mission envelope and policy-checked tool execution

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Any, Mapping


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class MissionEnvelope:
    run_id: str
    mission_id: str
    operator_id: str
    coalition_scope: frozenset[str]
    classification: str
    purpose: str
    expires_at: datetime

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


@dataclass(frozen=True)
class ToolRequest:
    envelope: MissionEnvelope
    tool_name: str
    arguments: Mapping[str, Any]

    @property
    def arguments_hash(self) -> str:
        stable = repr(sorted(self.arguments.items())).encode("utf-8")
        return "sha256:" + sha256(stable).hexdigest()


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    reason: str
    approval_role: str | None = None


def authorize_tool(request: ToolRequest, operator_compartments: set[str]) -> PolicyDecision:
    if request.envelope.is_expired():
        return PolicyDecision(Decision.DENY, "expired mission envelope")
    if request.envelope.classification.startswith("TOP_SECRET") and "TS" not in operator_compartments:
        return PolicyDecision(Decision.DENY, "operator lacks required compartment")
    if request.tool_name in {"action.prepare_package", "case.escalate"}:
        return PolicyDecision(Decision.REQUIRE_APPROVAL, "operationally significant action", "mission_commander")
    return PolicyDecision(Decision.ALLOW, "least-privilege tool execution permitted")
```

### Reproducible self-improvement evaluator

```python
from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prompt_input: str
    expected_labels: set[str]
    min_citation_count: int


@dataclass(frozen=True)
class EvalObservation:
    case_id: str
    predicted_labels: set[str]
    citation_count: int
    latency_ms: int
    unsupported_claims: int


@dataclass(frozen=True)
class EvalReport:
    precision: float
    recall: float
    citation_pass_rate: float
    p95_latency_ms: int
    unsupported_claim_rate: float
    approved_for_canary: bool


def evaluate_candidate(cases: list[EvalCase], observations: list[EvalObservation]) -> EvalReport:
    by_case = {obs.case_id: obs for obs in observations}
    precisions: list[float] = []
    recalls: list[float] = []
    citation_passes = 0
    latencies: list[int] = []
    unsupported = 0

    for case in cases:
        obs = by_case[case.case_id]
        true_positive = len(obs.predicted_labels & case.expected_labels)
        predicted = max(len(obs.predicted_labels), 1)
        expected = max(len(case.expected_labels), 1)
        precisions.append(true_positive / predicted)
        recalls.append(true_positive / expected)
        citation_passes += int(obs.citation_count >= case.min_citation_count)
        latencies.append(obs.latency_ms)
        unsupported += obs.unsupported_claims

    latencies.sort()
    p95_index = min(len(latencies) - 1, int(len(latencies) * 0.95))
    report = EvalReport(
        precision=mean(precisions),
        recall=mean(recalls),
        citation_pass_rate=citation_passes / len(cases),
        p95_latency_ms=latencies[p95_index],
        unsupported_claim_rate=unsupported / len(cases),
        approved_for_canary=False,
    )
    return EvalReport(
        **{**report.__dict__, "approved_for_canary": report.precision >= 0.91 and report.recall >= 0.86 and report.citation_pass_rate >= 0.98 and report.unsupported_claim_rate == 0 and report.p95_latency_ms <= 1800}
    )
```

### Change proposal guardrail

```python
def build_change_proposal(candidate_id: str, baseline: EvalReport, candidate: EvalReport, diff: str) -> dict[str, Any]:
    if not candidate.approved_for_canary:
        status = "rejected_by_eval_gate"
    elif candidate.precision < baseline.precision - 0.01:
        status = "rejected_precision_regression"
    else:
        status = "awaiting_human_approval"

    return {
        "proposal_id": f"chg_{candidate_id}",
        "organization": "ClearGlassInc Artemis",
        "status": status,
        "human_approval_required": True,
        "diff": diff,
        "baseline": baseline.__dict__,
        "candidate": candidate.__dict__,
        "rollback_target": "previous_signed_prompt_workflow_router_bundle",
        "apollo_ring": "mission-canary" if status == "awaiting_human_approval" else None,
    }
```
