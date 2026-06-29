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
