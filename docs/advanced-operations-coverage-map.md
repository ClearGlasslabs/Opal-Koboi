# ClearGlassInc Artemis Advanced Operations Coverage Map

**Audit date:** 2026-08-10  
**Scope:** repository evidence only; no production credentials, customer communication, billing, infrastructure, migration, provider, or deployment action was used.

## Rating standard

`OPTIMIZED` is reserved for a controlled workflow with ownership, validation and authorization, duplicate handling, timeout/retry/failure behavior, telemetry, audit, retention, user states, regression tests, recovery documentation, and passing evidence. `PARTIAL`, `UNTESTED`, `BLOCKED_BY_CREDENTIALS`, and `REQUIRES_OWNER_APPROVAL` identify missing evidence explicitly.

## Coverage map and job registry

| Workflow / control | Owner | Trigger | Safety controls and evidence | Status |
|---|---|---|---|---|
| Deterministic threat-model analysis | Artemis Security Architecture | Authenticated HTTP | Existing authorization and request telemetry; registry now defines 30-second timeout, one retry, idempotency, seven-year retention, audit, lifecycle, and rollback. Runtime adapter adoption by the existing route remains outstanding. | `PARTIAL` |
| External webhook delivery | Artemis Platform Operations | Event | Registry entry exists but the typed `external_webhooks` flag fails closed. No adapter or credential is connected and execution is suppressed with a metric and audit event. | `REQUIRES_OWNER_APPROVAL` |
| AI inference / copilots / agents | Artemis AI Governance | Manual proposal only | Typed `ai` flag defaults off. Existing deterministic intelligence modules do not grant operational authority. Credentials, eval acceptance, policy approval, and runtime integration are absent by design. | `BLOCKED_BY_CREDENTIALS` |
| Email and customer notifications | Customer Operations (unassigned) | None | Typed `email` flag defaults off; no delivery was implemented. Consent, templates, provider, monitoring, owner, and approval are absent. | `REQUIRES_OWNER_APPROVAL` |
| Billing / payment execution | Finance owner (unassigned) | None | Typed `billing` flag defaults off; architecture states orders remain schema-only. | `REQUIRES_OWNER_APPROVAL` |
| Live data ingestion | Data Operations (unassigned) | None | Typed `live_data` flag defaults off; no stream connection was made. Classification, coalition policy, source approval, credentials, SLOs, and backpressure validation are absent. | `BLOCKED_BY_CREDENTIALS` |
| Blue-team adapter | Security Operations (unassigned) | None | Typed `blue_team` flag defaults off; no real logs, alerts, infrastructure, or customer environment is accessed. | `REQUIRES_OWNER_APPROVAL` |
| Request observability | Artemis Platform Operations | Every API request | Existing middleware provides correlation and latency headers, request completion/failure logs, safe no-body logging, rate limiting, and security headers. Exported metrics and collector integration are not evidenced. | `PARTIAL` |
| Job observability and duplicate guard | Artemis Platform Operations | Governed job execution | New runtime emits JSON logs, counters, hashed idempotency evidence, correlation IDs, failure/success/disabled/duplicate audit events, and suppresses completed duplicates. Durable multi-replica storage and route adoption remain outstanding. | `PARTIAL` |
| Health/readiness | Artemis Platform Operations | HTTP probe | Existing health handler is present; critical queue/provider readiness cannot be claimed because providers and queues are intentionally disconnected. | `PARTIAL` |
| Operator job-monitoring route | Platform Operations | Operator HTTP | Not implemented: the current API-key role does not provide sufficiently granular operator authorization. Implementing a public-looking route would create risk rather than a safe control. | `REQUIRES_OWNER_APPROVAL` |

No row is classified `OPTIMIZED`: production durability, explicit route adoption, user-state evidence, or owner approval is incomplete.

## Implemented priority 1 — centralized typed job registry

### Current-state evidence

Before this patch, job behavior was distributed among route and service modules. `apps/api/ARCHITECTURE.md` documented service-level idempotency and audit invariants, but there was no single typed inventory containing owner, trigger, lifecycle, flag, timeout, retry, idempotency, retention, audit, and rollback fields.

### Gap and smallest complete fix

The missing control made it impossible to inspect every governed job against one enforceable schema. `app/core/job_registry.py` adds immutable `JobDefinition`, `RetryPolicy`, lifecycle/trigger enums, validation, unique-name enforcement, and a read-only registry. It records the existing deterministic analysis job and a safely disabled placeholder—not an integration—for outbound webhooks.

### Regression evidence and monitoring

Tests reject incomplete lifecycle definitions, verify required governance metadata, and ensure dead-letter state coverage. Registry construction fails at import time for invalid definitions. This is a static governance control, so execution telemetry belongs to the runtime rather than registry reads.

### Rollback

Revert `app/core/job_registry.py`, its imports/tests, and this document in one commit. The registry does not alter a database or existing route, so rollback has no data action. Preserve any audit evidence already emitted by callers.

## Implemented priority 2 — fail-closed feature flags

### Current-state evidence

The API settings had environment, database, credential, CORS, risk, and rate-limit fields, but no central typed safety decisions for AI, email, billing, live data, blue-team adapters, or external webhooks.

### Gap and smallest complete fix

Absent or malformed capability configuration could otherwise be interpreted inconsistently. `app/core/feature_flags.py` provides a closed enum, immutable snapshot, exact-boolean parsing, and an all-disabled singleton. It does not read credentials or enable anything.

### Regression evidence and monitoring

Tests enumerate every sensitive capability, prove the default is disabled, reject truthy strings, and prove snapshots cannot be mutated. Disabled job attempts produce both `disabled` metrics and audit events through the runtime.

### Rollback

Keep all providers disconnected, revert the feature-flag module/runtime references, and confirm no adapter has been separately approved. Because false is the only deployed state introduced here, rollback does not require configuration or data changes.

## Implemented priority 3 — job correlation, metrics, audit, and duplicate protection

### Current-state evidence

Request middleware already created or propagated request IDs and logged latency without bodies. Existing service mutations had domain-specific idempotency. There was no reusable job-level receipt connecting correlation, metrics, audit state, and duplicate suppression.

### Gap and smallest complete fix

Critical background/event workflows could be invoked without uniform job telemetry or a duplicate guard. `app/core/job_runtime.py` adds an explicit execution boundary that:

1. requires an idempotency key when declared by the registry;
2. hashes the key before logs/audit evidence;
3. suppresses completed duplicates;
4. prevents the operation from running under a disabled capability;
5. emits job/state counters and structured JSON success/failure logs;
6. emits audit records for completed, failed, disabled, and duplicate attempts; and
7. returns a correlated receipt with duration and lifecycle state.

The in-memory store is intentionally documented as process-local. It is deterministic and safe for single-process handlers, but must not be represented as distributed protection. A production adapter must use a transactional store and receive separate migration/owner approval.

### Regression evidence and monitoring

Tests prove a duplicate invokes the operation only once, raw keys do not enter audit evidence, disabled jobs never invoke operations, and provider-style failures are counted/audited and remain retryable. Metrics are dependency-free counters pending an owner-approved collector.

### Rollback

Stop routing new handlers through `JobRuntime`, revert its module/tests, and retain emitted audit records according to each job's retention rule. No database record, queue message, provider call, or infrastructure object was created by this patch.

## System Architecture

The target architecture retains strict boundaries: a TypeScript web workspace presents ontology-driven analyst views; the FastAPI control plane validates commands and applies policy; Foundry provides governed integration, transforms, Ontology objects/actions, lineage, and application logic; Gotham supports investigations, entity resolution, geotemporal tracking, and operational workflows; AIP hosts explicitly approved copilots, agents, tool policies, and evaluations; Apollo promotes signed versions across classified/coalition-aware environments with health gates and rollback. An event bus separates ingestion from bounded workers, while append-only audit receipts connect every derived artifact to source, policy decision, actor, and software version.

No Palantir connection is established here. These are deployment boundaries, not claims that a tenant, ontology, stream, or model is configured.

## Data and Ontology

Core objects are `Entity`, `Observation`, `Source`, `Relationship`, `Mission`, `Case`, `Alert`, `Assessment`, `Recommendation`, `Approval`, and `Outcome`. Every fact carries `valid_time`, `system_time`, confidence, source lineage, releasability, classification, compartments, coalition marking, and supersession state. Relationships are first-class temporal assertions rather than destructive overwrites. Ontology actions validate mission scope and policy before producing commands; agents receive only filtered object projections and citations, never unrestricted lake access.

## AI and Agent Design

AIP copilots may prepare—but not execute—triage, enrichment, correlation, summaries, case drafts, or action packages. Tools expose narrow typed queries and draft mutations. Policy gates require purpose, mission, actor, classification, compartments, and approval tier. Operationally significant actions stop at `manual_review_required`. The `ai` flag remains disabled until credentials, evaluation thresholds, prompt/model ownership, monitoring, red-team review, and explicit approval exist.

## Self-Improvement Loop

Operator corrections, accepted/rejected recommendations, alert dispositions, query outcomes, and mission results become versioned evaluation examples after minimization and authorization. Offline Python evaluation compares candidate prompt/workflow/router versions against a frozen baseline using precision, recall, unsupported-claim rate, latency, policy-denial rate, operator trust, calibration, and mission outcome proxies. Drift creates a review item. A candidate can only progress from `proposed` to `evaluated` to `approved` to canary; Apollo rollback pins the prior signed artifact. Agents may propose changes but cannot change objectives, policy, tools, approval thresholds, or their own deployed version.

## Full-Stack Implementation

The web layer consumes read models and renders loading, retrying, delayed, failed, dead-lettered, disabled, and manual-review states. FastAPI handles typed commands and correlation. Workers use the registry/runtime contract. Foundry datasets and Ontology provide lineage-preserving storage and actions; Gotham applications consume authorized objects. Search uses permission-filtered lexical/vector indexes. A model router is disabled by default and, if approved later, selects only allow-listed models by classification, latency, and evaluation profile. OpenTelemetry-compatible export and evaluation dashboards remain future integrations requiring approved endpoints.

## Security and Governance

Authentication is external to object authorization: every request also requires purpose-, mission-, entity-, row-, and column-level policy. Coalition boundaries are explicit release markings. Service identities are short-lived and tool-scoped. Logs redact payloads and idempotency secrets. Prompt, model, ontology, pipeline, policy, and application versions are signed and traceable. Immutable audit storage is a deployment requirement. No autonomous workflow receives authority to message customers, spend funds, change infrastructure, deploy, or access operational security data.

## Scenario Walkthrough

A future approved stream receives a signed observation and assigns source/correlation identifiers. Foundry validates schema, markings, lineage, and temporal state; Gotham links candidate entities without erasing uncertainty. A disabled-by-default AIP triage agent, once approved, would retrieve only mission-authorized context, cite facts, and draft a recommendation. Policy marks the action `manual_review_required`; a cleared operator rejects one association and approves the corrected draft. The correction becomes a minimized evaluation example, not an online model update. Offline evaluation proposes a new correlation threshold; reviewers inspect precision/recall and coalition slices, approve a bounded canary, and Apollo promotes the signed version. Drift or guardrail regression automatically restores the pinned version. Every transition shares correlation, version, actor, decision, and audit lineage.

## Deferred controls and approval gates

- Adopt a transactional idempotency store only after its schema, retention, concurrency behavior, and migration rollback are approved.
- Wire existing routes to the registry runtime in separate, bounded changes after service-specific timeout semantics are defined.
- Add an operator monitoring route only with a distinct operator role, non-public network policy, `noindex`, authorization-failure tests, and audit review.
- Do not connect Palantir, model, telemetry, email, payment, analytics, security, CRM, or webhook credentials without explicit owner approval.
- Do not deploy, migrate production, enable streams, or process data beyond existing authorization.

## Validation record

Commands were run from the paths shown on 2026-08-10. Results are captured here as reviewable repository evidence:

| Working directory | Command | Result | Exit code |
|---|---|---|---:|
| `apps/api` | `python -m ruff check app tests migrations` | All checks passed | 0 |
| `apps/api` | `python -m pytest -q` | 16 passed | 0 |
| repository root | `python -m ruff check .` | All checks passed | 0 |
| repository root | `python -m pytest -q` | 68 passed | 0 |
