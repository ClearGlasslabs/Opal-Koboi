# ClearGlassInc Artemis — Production Platform Architecture

## System Architecture

```text
 Operators / Commanders
          │ OIDC + WebAuthn
 ┌────────▼──────────┐      ┌──────────── Apollo ────────────┐
 │ Next.js Command UI│─────▶│ API gateway / zero-trust mesh  │
 └───────────────────┘      └──────────────┬─────────────────┘
                                           │ authenticated intent
 ┌──────── Gotham ────────┐     ┌──────────▼ AIP ────────────┐
 │ cases, tracks, maps,    │◀───▶│ executive planner, model   │
 │ investigations         │     │ router, governed agents    │
 └──────────┬──────────────┘     └──────────┬─────────────────┘
            │ ontology actions              │ typed proposals only
 ┌──────────▼ Foundry ──────────────────────▼─────────────────┐
 │ Ontology + lakehouse │ policy PDP/PEP │ Kafka event fabric │
 │ lineage + transforms │ approvals      │ schema registry    │
 └──────────┬────────────┴───────┬────────┴──────────┬────────┘
            │                    │                   │
     connectors/feeds     encrypted memory    telemetry/evals
```

Gotham is the operational investigation surface; Foundry integrates data and exposes governed Ontology objects/actions; AIP hosts evaluated copilots and agent workflows; Apollo promotes signed artifacts through environments with canaries, health gates, rollback, and runtime policy. These are integration boundaries, not claims that this repository contains Palantir products.

### Domain boundaries

| Domain | Ownership | Failure mode |
|---|---|---|
| `executive/` | mission state machines and typed event coordination | pause and queue proposals |
| `intelligence/` | fusion and read-only connector contracts | retain last known-good, mark stale |
| `cybersecurity/` | defensive signals and anomaly monitoring | isolate source, alert steward |
| `threat-intel/` | feed normalization and provenance | quarantine invalid feed |
| `agents/` | identities, capabilities, heartbeat, execution | revoke capability and fail closed |
| `policy/` | approval, authorization, sanitization, gating | deny |
| `memory/` | tenant/mission partitions and graph access | deny cross-partition reads |
| `telemetry/` | logs, traces, metrics, evals, chained audits | stop consequential actions |
| `ui/` | accessible command surfaces and secure confirmations | read-only fallback |

Services are stateless and horizontally scalable. Kafka-compatible partitions use `tenant_id:mission_id` keys. PostgreSQL/Foundry transactions hold control state; object storage is envelope-encrypted with tenant-scoped KMS keys. Consumers use idempotency keys, bounded retries, dead-letter quarantine, and backpressure. No model output directly invokes an operational action.

## Data and Ontology

Core objects are `Identity`, `Threat`, `Asset`, `ObservationEvent`, `Mission`, `Case`, `Evidence`, `Agent`, `Approval`, and `ChangeProposal`. Edges include `OBSERVED`, `ATTRIBUTED_TO`, `TARGETS`, `AFFECTS`, `MEMBER_OF`, `SUPPORTED_BY`, and `DERIVED_FROM`. Every object and edge carries:

```text
id, tenant_id, mission_ids, classification, compartments, releasable_to,
valid_from, valid_to, observed_at, confidence[0..1], source_uri,
content_hash, transformation_id, producer, ontology_version
```

Foundry Ontology actions are the only mutation path. Gotham views consume the same objects. Policy filtering occurs before retrieval so hidden entity existence cannot leak through counts or embeddings. Temporal edges preserve changing beliefs; evidence hashes and transformation lineage make every assertion reproducible. AIP tools receive object handles, not unrestricted SQL, and inherit entity markings.

## AI and Agent Design

The analyst copilot retrieves authorized evidence, explains uncertainty, drafts cited intelligence, and records corrections. The commander copilot compares courses of action but cannot approve one. A supervisor decomposes work into bounded tasks for triage, enrichment, correlation, summarization, and recommendation agents. Each agent has a signed registry identity, minimal permissions, mission-scoped memory, budgets, heartbeat, and explicit tool allowlist.

```text
PROPOSED → POLICY_CHECKED → RUNNING → EVIDENCE_REVIEW
    └deny→ REJECTED          │             │
                            └error→ SAFE_HALT
                                          ├low risk→ COMPLETED
                                          └high risk→ AWAITING_TWO_PERSON_APPROVAL
```

Tools return structured evidence with provenance. Opening a case is a governed Ontology action; generating a product creates a draft; exports, recommendations, external notifications, deployments, and any operationally meaningful change require approval. Tool arguments are validated before and after planning.

## Self-Improvement Loop

1. Capture privacy-minimized query traces, explicit ratings, corrections, alert dispositions, mission outcomes, latency, citations, and override reasons.
2. Join signals to immutable prompt/workflow/model versions and create representative, compartment-safe eval datasets.
3. An offline improvement agent proposes a bounded `ChangeProposal`; it cannot alter goals, policies, permissions, eval thresholds, or its own approval requirement.
4. Run regression, red-team, leakage, groundedness, precision/recall, latency, cost, calibration, operator-trust, and mission-impact evals.
5. Require code review plus data/model steward approval. High-risk changes require two people from separate roles.
6. Apollo signs and canaries the artifact to a small mission cohort. Drift monitors compare feature/output distributions and outcome quality against the control.
7. Promote only if hard safety floors and statistically meaningful objectives pass. Automatically roll back on safety, error-budget, latency, or trust regression.

Prompt and workflow A/B tests use deterministic cohort assignment and never mix coalition compartments. The audit ledger links proposal → evidence → eval run → approvals → artifact digest → deployment → outcome. Operators can reject suggestions; rejection becomes eval evidence, never an autonomous goal update.

## Full-Stack Implementation

```text
apps/web/             Next.js operator command surface
apps/api/             FastAPI gateway/control plane
executive/            orchestration + typed event bus reference
intelligence/         fusion, ontology, connectors, improvement pipeline
cybersecurity/        defensive monitoring boundary
threat-intel/         external feed boundary
agents/               secure registry and executors
policy/               policy decision point
memory/               graph and partition adapters
telemetry/            OpenTelemetry/audit/eval adapters
ui/                   UI contracts and design system boundary
```

Production event subjects follow `<domain>.<event>.v<major>`. Every envelope includes event, tenant, mission, producer, trace, timestamp, schema version, payload, and idempotency identifiers. Schema compatibility is checked in CI. Connector plugins are outbound-read-only workloads with signed images, egress allowlists, quotas, circuit breakers, cursor checkpoints, provenance validation, and quarantine queues.

## Security and Governance

OIDC workload/user identity and phishing-resistant MFA feed a policy decision point enforcing RBAC plus relationship/attribute-based need-to-know. Enforcement exists at gateway, service, Ontology action, search, and storage layers. Row, column, entity, edge, vector, and tool permissions share markings. Coalition release rules prohibit inference across partitions.

All traffic uses mTLS; data uses envelope encryption and HSM/KMS rotation. Nonces, timestamp windows, idempotency records, signed events, and consumer offsets resist replay. Rate limits apply per identity, tenant, mission, tool, and cost budget. Append-only hash-chained audit records export to immutable storage. Secrets and raw sensitive payloads never enter logs. Consequential operation requires fresh authorization, sanitized previews, purpose binding, and two-person approval. Missing policy, telemetry, identity, or key services cause deny/read-only safe mode.

## Scenario Walkthrough

At 02:14Z, a signed coalition feed connector emits `intelligence.observed.v1` for an anomalous infrastructure indicator. Fusion validates provenance, resolves two assets, and creates temporal `OBSERVED` edges at 0.71 confidence. The triage agent retrieves only mission-visible evidence and correlates three historical events; the correlation agent raises confidence to 0.86 with citations.

The recommendation agent drafts—not executes—a containment package. Policy scores it 82 and emits `require_approval`; the UI shows evidence, uncertainty, affected assets, sanitized tool arguments, and rollback plan. An operator corrects one identity match and a separate commander approves the revised package. A service re-authorizes at execution time, binds the approval ticket, records the ontology action, and emits an immutable outcome event.

After disposition, the correction, false-match feature, latency, approval edits, and outcome join the exact resolver/prompt versions. Offline evaluation finds a candidate threshold reduces false positives by 8% while recall stays above its safety floor. The improvement service opens a signed proposal. A steward approves a 5% Apollo canary; monitoring confirms the result, then promotion proceeds. If precision, leakage, latency, or trust regresses, Apollo restores the prior signed version and records the rollback. Artemis improves its resolver while its mission, authority, and safety constraints remain unchanged.
