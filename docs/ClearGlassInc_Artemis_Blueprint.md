# ClearGlassInc Artemis — Production Blueprint for a Self-Evolving Intelligence Platform

## System Architecture

### 1) End-to-End Layered Architecture (Palantir-aligned)

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│ Frontend Layer (React/Next.js + TypeScript + Map/Timeline UX)               │
│  - Analyst Workbench  - Commander Cockpit  - Case Console  - Approval Inbox │
└───────────────┬───────────────────────────────────────────────────────────────┘
                │ GraphQL/REST + WebSocket (mission updates)
┌───────────────▼───────────────────────────────────────────────────────────────┐
│ API & Trust Boundary (FastAPI Gateway)                                       │
│  - OIDC authn, JWT claims, mTLS, OPA/Rego PDP checks, request signing       │
└───────────────┬───────────────────────────────────────────────────────────────┘
                │
┌───────────────▼───────────────────────────────────────────────────────────────┐
│ Application Services (Python)                                                │
│  - Case Service  - Entity Service  - Mission Service  - ActionPkg Service    │
│  - Agent Orchestrator  - Policy Enforcement Point (PEP)                      │
└───────────────┬───────────────────────────────────────────────────────────────┘
                │ emits/consumes
┌───────────────▼───────────────────────────────────────────────────────────────┐
│ Event Fabric (Kafka/Pulsar)                                                  │
│  raw.signals -> enriched.signals -> intel.hypotheses -> action.recommend     │
└──────┬──────────────────────┬──────────────────────────────┬─────────────────┘
       │                      │                              │
┌──────▼───────┐      ┌───────▼────────┐            ┌────────▼─────────┐
│ Foundry      │      │ Gotham         │            │ AIP              │
│ Data fusion, │      │ Operations,    │            │ Agents, copilots,│
│ ontology,    │      │ investigations │            │ eval harness      │
│ pipelines    │      │ + case mgmt    │            │ + workflow auto   │
└──────┬───────┘      └───────┬────────┘            └────────┬─────────┘
       │                      │                               │
┌──────▼──────────────────────▼───────────────────────────────▼───────────────┐
│ Retrieval + Inference Layer                                                  │
│  - Hybrid search (graph + BM25 + vector)  - Model Router - Tool Runtime     │
└──────┬────────────────────────────────────────────────────────────────────────┘
       │
┌──────▼────────────────────────────────────────────────────────────────────────┐
│ Observability + Governance + Audit                                           │
│  OpenTelemetry, SIEM export, immutable provenance ledger, eval dashboards    │
└──────┬────────────────────────────────────────────────────────────────────────┘
       │
┌──────▼────────────────────────────────────────────────────────────────────────┐
│ Apollo Delivery Control                                                       │
│  staged deploy, canary, rollback, policy bundle promotion, runtime controls  │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 2) Runtime Responsibilities by Platform

- **Gotham**: operational intelligence UI, investigative case workflows, entity/activity timelines.
- **Foundry**: data integration, ontology lifecycle, batch/stream transforms, curated products.
- **AIP**: copilots, tool-using agents, evals, prompt/workflow candidates, safety orchestration.
- **Apollo**: secure deployment, phased rollouts, rollback, policy/model package pinning.

---

## Data and Ontology

### 1) Canonical Ontology (mission-grade)

Core entities:
- `Person`, `Organization`, `Device`, `Account`, `Asset`, `Location`
- `Signal`, `Event`, `Incident`, `Case`, `Mission`, `IntelProduct`, `ActionPackage`
- `SourceDocument`, `Observation`, `Indicator`, `Hypothesis`, `Decision`

Core relationships:
- `OBSERVED_AT`, `ATTRIBUTED_TO`, `OWNS`, `USES`, `ASSOCIATED_WITH`
- `DERIVED_FROM`, `SUPPORTS`, `CONTRADICTS`, `PART_OF_CASE`, `PART_OF_MISSION`
- `RECOMMENDS`, `APPROVED_BY`, `DISSEMINATED_TO`

Every node/edge includes:
- confidence + calibration bucket
- temporal fields: `valid_from`, `valid_to`, `ingested_at`, `last_verified_at`
- lineage: transformation IDs + source refs + tool provenance
- policy tags: classification, releasability, coalition caveats

### 2) SQL foundations (Foundry lakehouse style)

```sql
CREATE TABLE ontology_entity (
  entity_id            UUID PRIMARY KEY,
  entity_type          TEXT NOT NULL,
  canonical_name       TEXT NOT NULL,
  confidence_score     NUMERIC(5,4) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
  mission_context_id   UUID,
  classification       TEXT NOT NULL,
  releasability        TEXT NOT NULL,
  coalition_tags       TEXT[] NOT NULL,
  lineage_ref          TEXT NOT NULL,
  valid_from           TIMESTAMPTZ,
  valid_to             TIMESTAMPTZ,
  ingested_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_verified_at     TIMESTAMPTZ
);

CREATE TABLE ontology_relationship (
  rel_id               UUID PRIMARY KEY,
  src_entity_id        UUID NOT NULL REFERENCES ontology_entity(entity_id),
  dst_entity_id        UUID NOT NULL REFERENCES ontology_entity(entity_id),
  rel_type             TEXT NOT NULL,
  confidence_score     NUMERIC(5,4) NOT NULL,
  evidence_refs        TEXT[] NOT NULL,
  policy_scope         JSONB NOT NULL,
  valid_from           TIMESTAMPTZ,
  valid_to             TIMESTAMPTZ,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3) Ontology-driven behavior

- UI forms are generated from ontology schemas and mission constraints.
- Agent tools are dynamically filtered by ontology + policy context.
- Retrieval merges confidence, temporal relevance, and mission priority.
- Decision packages are linked to evidence graph paths for explainability.

---

## AI and Agent Design

### 1) Copilots

- **Analyst Copilot**: triage support, entity resolution explanations, case draft notes.
- **Commander Copilot**: mission impact forecast, risk-adjusted COA ranking.
- **Policy Copilot**: dissemination checks, releasability simulation, audit support.

### 2) Multi-agent workflow (AIP)

1. **Triage Agent**: normalize event + compute risk/confidence priors.
2. **Enrichment Agent**: gather graph context, historical analogs, and source corroboration.
3. **Correlation Agent**: detect campaign-level linkage across time and compartments.
4. **Recommendation Agent**: propose action package with evidence and uncertainty.
5. **Compliance Agent**: enforce policy and produce approval routing.

### 3) Tool-using action boundaries

Tool examples:
- `query_foundry_dataset`, `query_gotham_case`, `open_case`, `draft_intel_product`, `prepare_action_package`.

Operationally significant actions require gates:
- rule-based thresholds (risk, uncertainty, dissemination scope)
- two-person integrity for cross-coalition release
- explicit operator approval token before execution

---

## Self-Improvement Loop

### 1) Learning signal capture

Captured streams:
- operator edits (`feedback.operator_edits.v1`)
- recommendation outcomes (`feedback.alert_outcomes.v1`)
- case closure + mission KPI deltas (`mission.results.v1`)
- latency and failure traces (`runtime.telemetry.v1`)
- free-form trust ratings / comments

### 2) Controlled optimization workflow

```text
Collect -> Curate -> Evaluate -> Propose -> Review -> Canary -> Promote/Rollback
```

- **Collect**: feature store snapshots + labels from approved outcomes.
- **Curate**: de-bias, de-dup, compartment-safe dataset packaging.
- **Evaluate**: run prompt/workflow/model candidates against fixed eval suites.
- **Propose**: generate signed candidate bundle `candidate.{prompt,route,heuristic}.json`.
- **Review**: human change board approval (security + mission owner).
- **Canary**: Apollo deploy to 5–10% scoped traffic.
- **Promote/Rollback**: automatic rollback on KPI/policy regression.

### 3) Drift + rollback controls

- Data drift: PSI/KL divergence alarms on feature distributions.
- Prompt drift: semantic diff + safety regression tests.
- Policy drift: deny-by-default if policy package checksum mismatch.
- Rollback bundles include: model route, prompts, thresholds, policy refs.

---

## Full-Stack Implementation

### 1) Web UI

- React/Next.js + TypeScript.
- Mission timeline, entity graph explorer, alert triage queue, approval inbox.
- Live updates via WebSocket/GraphQL subscription.

### 2) API gateway and services

- FastAPI gateway with OIDC, JWT claim extraction, mTLS identity.
- Python async microservices with explicit idempotency keys.
- gRPC for low-latency internal service calls.

### 3) Event + storage + retrieval

- Kafka/Pulsar topics by lifecycle stage.
- Foundry lakehouse bronze/silver/gold tables.
- Graph projection for real-time entity traversal.
- Vector + keyword + graph hybrid retrieval.

### 4) Model router / inference

Routing features:
- mission criticality
- data classification
- latency SLO
- token budget + context length
- historical model reliability by task type

### 5) Observability and eval dashboards

- OpenTelemetry spans across agent/tool hops.
- Prometheus/Grafana for latency, throughput, queue lag.
- Evals dashboard: precision/recall, operator trust, policy violation rate.

---

## Security and Governance

- Need-to-know ABAC + RBAC + relationship-aware controls.
- Row/column/entity-level policy enforcement.
- Coalition compartments with releasability caveats.
- Zero-trust service identity, short-lived credentials, signed artifacts.
- Immutable provenance ledger for data/model/prompt/action lineage.
- Policy-as-code (OPA/Rego), prompt governance, model registry governance.

---

## Code Examples (Python-forward)

### 1) FastAPI gateway with policy check

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="ClearGlassInc Artemis Gateway")

class AlertIn(BaseModel):
    mission_id: str
    signal_id: str
    severity_hint: float

async def opa_allow(subject: dict, action: str, resource: dict) -> bool:
    payload = {"input": {"subject": subject, "action": action, "resource": resource}}
    async with httpx.AsyncClient(timeout=2.0) as client:
        r = await client.post("http://opa:8181/v1/data/artemis/allow", json=payload)
        r.raise_for_status()
        return bool(r.json().get("result", False))

@app.post("/alerts/triage")
async def triage_alert(alert: AlertIn, user=Depends(lambda: {"id": "u-1", "roles": ["analyst"]})):
    allowed = await opa_allow(user, "triage:write", {"mission_id": alert.mission_id})
    if not allowed:
        raise HTTPException(403, "Denied by policy")
    return {"status": "accepted", "signal_id": alert.signal_id}
```

### 2) Streaming event handler (triage)

```python
from dataclasses import dataclass
from confluent_kafka import Consumer, Producer
import json

@dataclass
class TriageResult:
    signal_id: str
    risk_score: float
    confidence: float
    reason_codes: list[str]

consumer = Consumer({"bootstrap.servers": "kafka:9092", "group.id": "triage-v1"})
producer = Producer({"bootstrap.servers": "kafka:9092"})
consumer.subscribe(["raw.signals.v1"])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    payload = json.loads(msg.value())
    risk = min(1.0, 0.6 * payload.get("anomaly", 0) + 0.4 * payload.get("threat", 0))
    out = TriageResult(payload["signal_id"], risk, 0.82, ["ANOMALY_PATTERN", "KNOWN_IOC"])
    producer.produce("triage.signals.v1", json.dumps(out.__dict__).encode("utf-8"))
    producer.flush()
```

### 3) Ontology-aware query function

```python
from sqlalchemy import text

def fetch_case_graph(conn, case_id: str, max_depth: int = 2):
    sql = text("""
    WITH RECURSIVE g AS (
      SELECT e.entity_id, e.entity_type, e.canonical_name, 0 AS depth
      FROM ontology_entity e
      JOIN case_entity ce ON ce.entity_id = e.entity_id
      WHERE ce.case_id = :case_id
      UNION ALL
      SELECT e2.entity_id, e2.entity_type, e2.canonical_name, g.depth + 1
      FROM g
      JOIN ontology_relationship r ON r.src_entity_id = g.entity_id
      JOIN ontology_entity e2 ON e2.entity_id = r.dst_entity_id
      WHERE g.depth < :max_depth
    )
    SELECT * FROM g;
    """)
    return conn.execute(sql, {"case_id": case_id, "max_depth": max_depth}).mappings().all()
```

### 4) Agent workflow state machine

```python
from enum import Enum

class Stage(str, Enum):
    TRIAGE = "triage"
    ENRICH = "enrich"
    CORRELATE = "correlate"
    RECOMMEND = "recommend"
    APPROVAL = "approval"
    EXECUTE = "execute"

TRANSITIONS = {
    Stage.TRIAGE: Stage.ENRICH,
    Stage.ENRICH: Stage.CORRELATE,
    Stage.CORRELATE: Stage.RECOMMEND,
    Stage.RECOMMEND: Stage.APPROVAL,
    Stage.APPROVAL: Stage.EXECUTE,
}

def next_stage(stage: Stage, approved: bool) -> Stage:
    if stage == Stage.APPROVAL and not approved:
        return Stage.TRIAGE
    return TRANSITIONS[stage]
```

### 5) Eval pipeline for prompt/workflow candidates

```python
from dataclasses import dataclass

@dataclass
class EvalMetrics:
    precision: float
    recall: float
    p95_latency_ms: int
    trust_score: float
    policy_violations: int

BASELINE = EvalMetrics(0.84, 0.79, 820, 4.2, 0)

def passes_gate(candidate: EvalMetrics) -> bool:
    return (
        candidate.precision >= BASELINE.precision + 0.01
        and candidate.recall >= BASELINE.recall
        and candidate.p95_latency_ms <= BASELINE.p95_latency_ms + 50
        and candidate.trust_score >= BASELINE.trust_score
        and candidate.policy_violations == 0
    )
```

---

## Scenario Walkthrough (Live Mission)

1. **Ingress (T+0s)**: a suspicious maritime signal enters `raw.signals.v1` for Mission `M-884`.
2. **Triage (T+2s)**: Triage Agent scores risk `0.92`, confidence `0.81`, opens provisional case in Gotham.
3. **Enrichment (T+7s)**: Enrichment Agent links vessel account to sanctioned shell network (confidence `0.76`).
4. **Correlation (T+11s)**: Correlation Agent finds three similar route deviations in 48 hours.
5. **Recommendation (T+15s)**: Recommendation Agent proposes Action Package `AP-221` with two COAs.
6. **Approval Gate (T+18s)**: Compliance Agent flags cross-coalition dissemination; operator approval required.
7. **Human Decision (T+26s)**: commander approves COA-2, edits dissemination list.
8. **Execution (T+33s)**: action package published; audit entries sealed with provenance hash.
9. **Outcome (T+3h)**: mission success confirmed; false-positive risk reduced by operator correction notes.
10. **Self-Improvement (nightly)**:
    - feedback + outcome converted into labeled eval rows,
    - candidate prompt/workflow route generated,
    - eval passes (precision +2.3%, p95 latency +18ms, violations 0),
    - Apollo canary at 10% traffic,
    - promotion after 24h stability.

This is how **ClearGlassInc Artemis** gets better continuously while staying human-governed, policy-bounded, and operationally safe.
