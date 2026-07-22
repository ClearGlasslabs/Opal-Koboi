# ARTEMIS // FAWL Remediation Ledger

This ledger records verified repository evidence as of 2026-07-21 on branch `work`. It does not claim live deployments, customers, certifications, or operational status.

## Architecture Map

- Root Python package `intelligence/`: local-first defensive intelligence primitives, policy checks, self-improvement proposal gates, deployment handoff plans, and incident recovery controls.
- FastAPI service `apps/api/app/`: modular API routes for health, events, approvals, products, inventory, and autonomous threat modeling.
- Next.js application `apps/web/`: marketing/landing UI for the browser intelligence assistant.
- Security policy assets `security/`: CI policy JSON and guard script.
- Documentation `docs/`, `README.md`, and `artemis-blueprint.md`: architecture, supply-chain guidance, audit findings, and Palantir-oriented implementation blueprint.

## Baseline Verification Evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Python tests | Pass | `python -m pytest -q` reported 29 passed before changes and 33 passed after changes. |
| Python lint | Pass | `python -m ruff check .` reported all checks passed before and after changes. |
| Web dependency/build/lint | Blocked | `cd apps/web && npm install && npm run build && npm run lint` failed at `npm install` with npm registry `403 Forbidden` for `@types/node`; no web build claim is made. |
| Deployment | Not run | No credentials, deployment target, signed artifact key, or Apollo runtime is present in this repository. |
| Secrets review | Partial | Static inspection found no intentionally added secrets; comprehensive secret scanning tooling is not configured in this repo. |

## Ranked Findings

| Rank | Finding | Evidence / affected files | Risk | Commercial impact | Effort | Dependencies | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | Autonomous recovery actions needed a deterministic lifecycle envelope separate from AI output. | Added `intelligence/artemis_incident_control.py` and tests in `tests/test_artemis_incident_control.py`. | Unbounded recovery could worsen incidents or hide accountability. | Required for paid pilots in regulated operations. | Medium | Persistent audit store, queue worker integration. | Every action has validated evidence, idempotency key, timeout, blast-radius ceiling, rollback strategy, human approval where required, and tamper-evident receipt. |
| P0 | Web production build cannot be verified in this environment. | `apps/web/package.json`; npm registry returned `403 Forbidden` for `@types/node`. | Release confidence is incomplete. | Blocks credible production demo unless dependencies are vendored/cached or registry access is fixed. | Low-Medium | npm registry access or committed lockfile/cache policy. | `npm ci`, `npm run build`, and `npm run lint` pass in CI. |
| P1 | Deployment and rollback remain plan-only. | `intelligence/artemis_deploy_execute.py` builds Apollo-style commands but does not execute Apollo. | Operators may mistake handoff plans for live deployment automation. | Limits revenue-ready claims until integrated with real release controller. | High | Apollo or equivalent controller, signing keys, SBOM/provenance. | Signed artifact verification, canary, observe, and rollback are executed and independently audited in CI/CD. |
| P1 | Incident memory, poisoning defenses, and retrieval provenance are documented but not end-to-end integrated. | `artemis-blueprint.md`, `docs/*`, local Python primitives. | AI-assisted RCA may over-trust polluted signals. | Reduces trust for security-sensitive pilots. | High | Vector/search store, lineage model, eval harness. | Retrieval results include provenance, freshness, source trust, poison flags, and exclusion reasons. |
| P1 | Policy-as-code is implemented as Python policy, not external OPA/Rego bundles. | `intelligence/artemis_policy.py`. | Policy distribution/versioning is harder across services. | Enterprise buyers expect auditable centralized policy lifecycle. | Medium | OPA or Cedar integration, policy CI. | Policy bundles are signed, tested, versioned, and enforced at API and worker boundaries. |
| P2 | API service lacks full incident-lifecycle routes/workers. | `apps/api/app/api/route_handlers/`, `apps/api/app/services/`. | Controls cannot yet be exercised through the platform API. | Slower pilot onboarding. | Medium | Database migrations and auth integration. | API exposes incident creation, evidence append, action evaluation, and receipt retrieval with RBAC tests. |
| P2 | Supply-chain controls are guidance-heavy. | `SECURITY.md`, `security/ci_guard.py`, `docs/supply-chain-control-plane.md`. | Dependency compromise may go undetected. | Enterprise procurement friction. | Medium | SBOM tooling, Sigstore/cosign. | CI emits SBOM, verifies pinned deps, signs artifacts, and fails on critical vulnerabilities. |
| P3 | Commercial pilot packaging is documented but not automated. | `README.md`, `docs/*`. | Sales cycle relies on manual setup. | Delays revenue capture. | Medium | Demo deployment, metering backend, license terms. | Reproducible pilot installer, usage metering, onboarding checklist, and value dashboard. |

## Recovery-Control Matrix

| Lifecycle phase | Control | Current status |
| --- | --- | --- |
| DETECT | Event evidence model with source, hash, confidence, provenance | Implemented as pure Python model. |
| VALIDATE | Confidence threshold and content hash validation | Implemented. |
| CORRELATE | Incident context includes correlated event IDs and affected assets | Implemented model-level support. |
| CLASSIFY | Deterministic severity classifier | Implemented and tested. |
| CONTAIN | Containment actions require scope, timeout, idempotency, rollback | Implemented and tested. |
| PLAN | Recovery action schema forces blast-radius ceiling and rollback strategy | Implemented and tested. |
| AUTHORIZE | High-impact incidents require human approval metadata | Implemented and tested. |
| EXECUTE | Dispatch is not performed by the model; callers must enforce decision | Implemented as gate only. |
| VERIFY | Independent verification obligation emitted for each allowed action | Implemented as obligation. |
| MONITOR | Trace/mission/idempotency propagation obligation emitted | Implemented as obligation. |
| CLOSE/ROLLBACK/ESCALATE | Rollback and escalation action types are represented | Implemented model-level support. |

## Deployment Guide

1. Install Python dependencies and run `python -m pytest -q` plus `python -m ruff check .`.
2. Restore npm registry access or a trusted dependency cache, then run `cd apps/web && npm ci && npm run build && npm run lint`.
3. Generate and attach SBOM/provenance for Python and web artifacts.
4. Sign artifacts and verify signatures before canary release.
5. Deploy first to shadow/canary with human approval gates enabled.
6. Monitor precision, recall, unsupported-claim rate, p95 latency, policy-denial rate, and operator trust.
7. Roll back automatically on halt-level drift, SLO breach, approval-gate failure, or audit-write failure.

## Commercial Pilot Plan

- Package a 30-day paid pilot around defensive incident triage, evidence preservation, and governed recovery recommendations.
- Success metrics: mean time to classify, mean time to contain, percentage of cited recommendations, false-positive reduction, policy-denial correctness, operator trust, and audit receipt completeness.
- Pilot boundaries: no offensive access, no autonomous high-impact remediation without human approval, no customer-secret ingestion without configured KMS/HSM, and no claims of deployment until customer environment verification passes.
- Deliverables: tenant setup, mission taxonomy, RBAC/SSO mapping, incident replay drill, dashboard walkthrough, rollback drill, weekly value report, and final production-readiness report.
