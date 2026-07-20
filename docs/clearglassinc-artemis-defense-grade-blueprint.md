# ClearGlassInc Artemis — Defense-Grade Self-Evolving AI Intelligence Platform

This blueprint defines a production-safe, human-governed architecture for **ClearGlassInc Artemis** on Palantir Gotham, Foundry, AIP, and Apollo. It is intentionally Python-first for deterministic policy, evaluation, routing, and workflow logic.

## System Architecture

ClearGlassInc Artemis is split into audited planes with explicit trust boundaries:

| Plane | Responsibility | Palantir anchor | Implementation pattern |
|---|---|---|---|
| Experience | Analyst cockpit, commander brief, feedback console, eval review | Gotham operational applications, Foundry applications | Next.js/React, typed API clients, WebSocket/SSE alert streams |
| Access | Identity, mission context, request signing, policy decisions | Foundry security model | OIDC/SAML, ABAC, OPA/Rego, short-lived tool tokens |
| Operations | Cases, alerts, entity timelines, action packages | Gotham | Case service, alert service, action package service, audit service |
| Data | Ingestion, transforms, lakehouse, quality checks | Foundry | streaming ingest, dataset transforms, schema contracts, data quality tests |
| Ontology | Entities, links, confidence, lineage, temporal state | Foundry Ontology and Gotham entity tracking | mission-scoped graph APIs, typed relationships, entity-level permissions |
| Intelligence | Copilots, agents, evals, prompt/workflow/model routing | AIP | tool registry, model router, state machines, eval harnesses |
| Release | deployment, canary, rollback, runtime policy | Apollo | signed containers, SBOMs, progressive deployment, kill switches |
| Observability | metrics, traces, immutable audit, model quality | Foundry telemetry, Apollo runtime | OpenTelemetry, SIEM export, eval dashboards, append-only logs |

End-to-end flow:

1. Live and historical feeds enter Foundry through streaming and batch connectors.
2. Foundry validates schema, attaches source lineage, deduplicates, and maps records into the ontology.
3. Gotham surfaces operational entities, cases, alerts, and timelines to analysts.
4. AIP agents receive only policy-filtered mission views and use signed tools for retrieval, enrichment, summarization, and recommendations.
5. Humans approve operationally significant outputs before release, tasking, external sharing, or case escalation.
6. Feedback, outcomes, and telemetry are converted into evaluation data.
7. Improvement proposals are versioned, reviewed, canaried through Apollo, and rolled back automatically if guardrails fail.

## Data and Ontology

The ontology is the control surface for both human workflows and agent behavior. It prevents free-form AI access to raw data by forcing every action through typed, permissioned objects.

### Core entities

| Entity | Key fields | Purpose |
|---|---|---|
| `Mission` | `mission_id`, `classification`, `coalition_scope`, `objectives`, `approval_matrix`, `valid_from`, `valid_to` | Bounds every query, tool call, workflow, and release decision. |
| `IntelEvent` | `event_id`, `source_id`, `payload_hash`, `observed_at`, `ingested_at`, `classification`, `lineage_refs` | Immutable normalized signal from live or historical data. |
| `TrackedEntity` | `entity_id`, `entity_type`, `aliases`, `confidence`, `risk_score`, `compartments`, `release_markings` | Person, organization, infrastructure, location, device, account, or asset. |
| `Relationship` | `src_entity_id`, `dst_entity_id`, `relation_type`, `confidence`, `valid_time`, `evidence_ids` | Temporal evidence-backed relationship between entities. |
| `Alert` | `alert_id`, `severity`, `reason_codes`, `dedupe_key`, `status`, `recommended_next_step` | Triage artifact derived from events and entity context. |
| `Case` | `case_id`, `mission_id`, `priority`, `status`, `linked_entities`, `assigned_cell` | Investigation container used by Gotham workflows. |
| `AgentRun` | `run_id`, `workflow_version`, `prompt_version`, `model_id`, `tool_calls`, `policy_decisions`, `output_hash` | Governance record for each AI execution. |
| `FeedbackSignal` | `signal_id`, `target_type`, `target_id`, `operator_id`, `label`, `correction`, `outcome`, `trust_score` | Learning input that never directly changes production behavior. |
| `ChangeProposal` | `proposal_id`, `change_type`, `diff_hash`, `eval_delta`, `risk_score`, `approval_status`, `rollback_plan` | Human-reviewed candidate for prompt, workflow, routing, or heuristic updates. |

Ontology invariants:

- Every assertion has source lineage, confidence, classification, release marking, ingest time, and valid time.
- Current truth, historical truth, and projected risk are separate fields, never overwritten silently.
- Coalition release is explicit; membership in a role does not imply releasability.
- Agents cannot perform unrestricted graph traversal. Tools enforce mission scope, purpose binding, row/column/entity permissions, and query budgets.

## AI and Agent Design

ClearGlassInc Artemis uses AIP for controlled copilots and tool-using agents:

- **Analyst Copilot:** explains alerts, cites evidence, drafts RFIs, highlights uncertainty, and asks for missing context.
- **Commander Copilot:** summarizes mission posture, risk deltas, resource impacts, and confidence caveats.
- **Data Steward Copilot:** detects drift, stale sources, ontology quality gaps, and lineage breaks.
- **Eval Steward Copilot:** reviews proposed self-upgrades and converts eval results into human-readable risk summaries.

Multi-agent workflow pattern:

1. **Triage Agent** creates or suppresses alerts using deterministic dedupe, severity scoring, and evidence thresholds.
2. **Enrichment Agent** gathers permitted context through sanctioned tools only.
3. **Correlation Agent** proposes graph links with confidence and evidence, but high-impact assertions require review.
4. **Summarization Agent** drafts products with citation coverage checks and redaction.
5. **Recommendation Agent** prepares action packages; it cannot execute operational actions.
6. **Improvement Agent** proposes prompt/workflow/router changes after offline evals; it cannot deploy them.

Approval gates are mandatory for external disclosure, case escalation, tasking recommendations, changes to model routing, workflow updates, prompt releases, policy exceptions, and any action package that could affect real-world operations.

## Self-Improvement Loop

Self-improvement is a governed software-release process, not autonomous goal mutation.

### Signal capture

ClearGlassInc Artemis captures:

- operator edits to summaries, severity, entities, relationships, and recommended actions;
- analyst accept/reject decisions and rationale;
- alert outcomes such as true positive, false positive, duplicate, stale, escalated, or unresolved;
- query latency, empty-result rates, policy denials, tool failures, and timeout rates;
- mission metrics including time-to-triage, time-to-brief, trust score, and outcome quality;
- model metrics including unsupported claim rate, citation coverage, refusal quality, and hallucination flags.

### Improvement pipeline

1. **Normalize:** redact sensitive text, validate labels, and write immutable `FeedbackSignal` rows.
2. **Freeze eval sets:** create stratified test suites across missions, sources, classifications, languages, and edge cases.
3. **Generate candidates:** propose prompt diffs, workflow thresholds, retrieval settings, or router rules.
4. **Evaluate offline:** run precision, recall, latency, citation, safety, policy, and drift checks.
5. **Score risk:** block candidates that degrade critical metrics, increase unsafe action probability, or cross policy boundaries.
6. **Human review:** route `ChangeProposal` to mission owner, model steward, and security approver.
7. **Canary:** Apollo deploys to a limited cohort with automated rollback triggers.
8. **Promote or rollback:** promotion requires sustained improvement and no guardrail breach.

Safe-update constraints:

- No candidate can change mission goals, approval gates, classification policy, or coalition boundaries.
- Prompt and workflow candidates are content-addressed and versioned.
- Rollback plans are generated before deployment.
- Drift detection compares production traffic to eval distributions and opens a review task when divergence exceeds thresholds.

## Full-Stack Implementation

Reference services:

```text
apps/
  web/                    # Analyst cockpit and commander dashboard
  api/                    # FastAPI gateway and domain services
  workers/                # Temporal/Celery workflow workers
  evals/                  # Offline eval runners and dashboards
packages/
  policy/                 # Rego/Cedar policies and tests
  ontology/               # typed ontology schemas and query clients
  agents/                 # AIP prompts, tools, routers, and workflow graphs
infra/
  apollo/                 # deployment specs, canary policy, rollback config
  observability/          # OpenTelemetry, dashboards, SIEM routing
```

Request contracts are typed, signed, and purpose-bound. The API gateway builds an authorization context, the policy layer filters data before retrieval, and every agent tool call is recorded as an `AgentRun` child event.

## Security and Governance

Security controls:

- need-to-know ABAC using mission, role, compartment, clearance, release marking, purpose, and time window;
- row, column, entity, and relationship-level policy enforcement;
- coalition boundaries implemented as explicit releasability labels;
- zero-trust service-to-service calls with mTLS, workload identity, and short-lived credentials;
- immutable audit logs for ingest, query, tool call, model response, operator decision, approval, deployment, and rollback;
- prompt governance with versioning, review, red-team evals, and provenance;
- model governance with approved model inventory, routing policy, eval evidence, and retirement criteria;
- policy-as-code tests in CI and runtime policy decision logging.

## Code Examples

### Python policy check

```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class AuthContext:
    user_id: str
    mission_id: str
    clearance: str
    compartments: set[str]
    coalition: set[str]
    purpose: str

@dataclass(frozen=True)
class OntologyObject:
    object_id: str
    classification: str
    compartments: set[str]
    releasable_to: set[str]
    mission_ids: set[str]
    valid_until: datetime | None


def can_read(ctx: AuthContext, obj: OntologyObject) -> bool:
    if ctx.mission_id not in obj.mission_ids:
        return False
    if obj.valid_until and obj.valid_until < datetime.now(timezone.utc):
        return False
    if not obj.compartments.issubset(ctx.compartments):
        return False
    if obj.releasable_to and not obj.releasable_to.intersection(ctx.coalition):
        return False
    return ctx.purpose in {"triage", "investigation", "briefing", "eval_review"}
```

### Python ontology-driven query

```python
async def get_authorized_entity_timeline(db, ctx: AuthContext, entity_id: str) -> list[dict]:
    rows = await db.fetch_all(
        """
        SELECT event_id, observed_at, summary, classification, compartments,
               releasable_to, mission_ids, confidence, lineage_refs
        FROM ontology_entity_timeline
        WHERE entity_id = :entity_id
        ORDER BY observed_at DESC
        LIMIT 500
        """,
        {"entity_id": entity_id},
    )
    return [row for row in rows if can_read(ctx, row_to_ontology_object(row))]
```

### Python workflow state machine

```python
from enum import StrEnum

class AlertState(StrEnum):
    RECEIVED = "received"
    DEDUPED = "deduped"
    ENRICHED = "enriched"
    CORRELATED = "correlated"
    DRAFTED = "drafted"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

ALLOWED_TRANSITIONS = {
    AlertState.RECEIVED: {AlertState.DEDUPED},
    AlertState.DEDUPED: {AlertState.ENRICHED, AlertState.REJECTED},
    AlertState.ENRICHED: {AlertState.CORRELATED},
    AlertState.CORRELATED: {AlertState.DRAFTED},
    AlertState.DRAFTED: {AlertState.AWAITING_APPROVAL},
    AlertState.AWAITING_APPROVAL: {AlertState.APPROVED, AlertState.REJECTED},
}


def transition(current: AlertState, desired: AlertState) -> AlertState:
    if desired not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"illegal transition: {current} -> {desired}")
    return desired
```

### Python eval gate for self-upgrades

```python
@dataclass(frozen=True)
class EvalResult:
    precision: float
    recall: float
    p95_latency_ms: int
    unsupported_claim_rate: float
    policy_violation_count: int
    operator_trust_delta: float


def approve_candidate(base: EvalResult, candidate: EvalResult) -> bool:
    if candidate.policy_violation_count != 0:
        return False
    if candidate.unsupported_claim_rate > min(base.unsupported_claim_rate, 0.01):
        return False
    if candidate.precision < base.precision + 0.02:
        return False
    if candidate.recall < base.recall - 0.005:
        return False
    if candidate.p95_latency_ms > int(base.p95_latency_ms * 1.10):
        return False
    return candidate.operator_trust_delta >= 0
```

### TypeScript tool-call contract

```ts
export type ToolEnvelope = {
  runId: string;
  missionId: string;
  operatorId: string;
  tool: "ontology.query" | "case.open" | "intel.draft" | "eval.run";
  purpose: "triage" | "investigation" | "briefing" | "eval_review";
  classification: string;
  argumentsHash: string;
  policyToken: string;
  expiresAt: string;
};

export async function callTool<TArgs, TResult>(
  envelope: ToolEnvelope,
  args: TArgs,
): Promise<TResult> {
  const res = await fetch("/api/tools/execute", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ envelope, args }),
  });
  if (!res.ok) throw new Error(`tool call failed: ${res.status}`);
  return (await res.json()) as TResult;
}
```

### SQL lineage-first event table

```sql
CREATE TABLE intel_event (
  event_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  classification TEXT NOT NULL,
  compartments TEXT[] NOT NULL DEFAULT '{}',
  releasable_to TEXT[] NOT NULL DEFAULT '{}',
  mission_ids TEXT[] NOT NULL,
  confidence NUMERIC(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  lineage_refs JSONB NOT NULL,
  normalized_payload JSONB NOT NULL
);
```

## Scenario Walkthrough

A live infrastructure telemetry event enters Foundry at 03:14:22Z with a payload hash, source lineage, and coalition release marking. Foundry validates the schema, detects that the event references a previously tracked infrastructure entity, and writes an `IntelEvent` plus an evidence-backed `OBSERVED_IN` relationship.

The Triage Agent receives a mission-scoped task envelope. It queries only authorized ontology views, finds two similar events in the last six hours, deduplicates one stale duplicate, and creates a medium-severity `Alert` with reason codes and citations. The Enrichment Agent adds permitted context from internal datasets. The Correlation Agent proposes a relationship to an existing case but marks the confidence as provisional because one source has degraded freshness.

The Summarization Agent drafts a short intelligence product with citations and uncertainty notes. The Recommendation Agent prepares an action package recommending analyst review, additional collection, and commander notification. Because the package is operationally significant, it moves to `AWAITING_APPROVAL` and cannot execute automatically.

An operator rejects one inferred relationship, downgrades severity, and approves the rest of the package. The correction becomes a `FeedbackSignal` linked to the `AgentRun`, alert, relationship candidate, mission, and final outcome. Overnight, the Improvement Agent tests a threshold adjustment and prompt clarification against frozen evals. Precision improves, recall remains stable, unsupported claims do not increase, and latency stays within budget. The system creates a `ChangeProposal`, human reviewers approve it, and Apollo canaries the update to a small analyst cohort. If false positives or policy denials rise, Apollo rolls back to the previous workflow version and opens a review ticket with the full audit trail.
