# ClearGlassInc Artemis — AEGIS Federal Control Plane

> **Status:** production implementation blueprint, not legal advice. Regulatory
> mappings must be versioned and approved by Canadian counsel before activation.

## System Architecture

AEGIS Federal is an assurance application on the ClearGlassInc Artemis fabric.
It converts connector observations into a continuously evaluated evidence graph:

```text
M365 / Azure / AWS / GitHub / EDR / SIEM / policies / vendors
                │ signed, tenant-scoped events
                ▼
Foundry pipelines → Ontology objects/actions → evidence graph
                │                         │
                ▼                         ▼
        AIP evaluation agents      Gotham investigation
                │ typed proposals         │ cases/owners
                └──────────┬──────────────┘
                           ▼
             Requirement → Control → System → Evidence
                         → Owner → Risk → Remediation
                           │
                           ▼
           Apollo-signed dashboard and evidence bundles
```

Foundry owns integration, lineage, Ontology objects, and governed actions.
Gotham provides investigations, entity tracking, and operational case views.
AIP hosts bounded copilots, agents, and evaluations; it never declares legal
compliance or directly executes a consequential action. Apollo promotes signed
artifacts through development, validation, canary, and production rings with
health-gated rollback.

## Data and Ontology

Primary objects are `Requirement`, `Control`, `System`, `Evidence`, `Owner`,
`Risk`, `Remediation`, `Vendor`, `Attestation`, `Incident`, `Approval`, and
`EvidenceBundle`. Relationships include `IMPLEMENTS`, `SUPPORTS`, `OPERATES_ON`,
`OWNED_BY`, `INTRODUCES`, `MITIGATED_BY`, `VERIFIED_BY`, and `SUPPLIED_BY`.

Every object carries tenant, mission, classification, compartments, coalition
release markings, valid/observed time, confidence, source URI, content hash,
transform version, and Ontology version. Evidence is append-only; a new
observation supersedes rather than mutates prior temporal truth. Retrieval and
vector indexing occur *after* authorization filtering so hidden entities cannot
leak through similarity scores, counts, or generated text.

The executable reference in
`intelligence/artemis_compliance_control_plane.py` provides counsel-approved
requirements, deterministic evidence sufficiency evaluation, mission isolation,
finding ownership, content-addressed reports, and two-person export gating.

## AI and Agent Design

The analyst copilot answers graph-grounded questions and cites evidence handles.
The executive copilot drafts risk registers and board narratives. Specialized
agents perform connector triage, evidence normalization, entity resolution,
control correlation, vendor deterioration detection, gap summarization, and
remediation drafting. Tools expose narrow Ontology queries and actions rather
than unrestricted SQL or cloud credentials.

```text
OBSERVED → NORMALIZED → POLICY_CHECKED → CORRELATED → HUMAN_REVIEW
               │ deny                         │
               └── QUARANTINED                ├── accept → VERIFIED
                                              └── reject → CORRECTION
```

Agents may draft a case, evidence request, questionnaire, remediation, or action
package. External notification, vendor rating publication, regulator export,
production change, and operational response require fresh purpose-bound policy
authorization and the configured human approval quorum.

## Self-Improvement Loop

1. Capture ratings, corrections, query traces, alert dispositions, vendor
   outcomes, evidence aging, incident results, edits, latency, and overrides.
2. Join every signal to exact prompt, workflow, catalogue, router, model, data,
   and policy versions; remove operator identity and unauthorized compartments.
3. Build immutable development and holdout eval sets without cross-mission
   contamination.
4. Permit an offline improvement agent to propose only bounded prompt, workflow,
   heuristic, or routing diffs. Goals, permissions, policy floors, approval
   rules, and eval thresholds are immutable to the agent.
5. Evaluate precision, recall, false-negative cost, citation coverage,
   groundedness, calibration, leakage, p95 latency, spend, operator trust, and
   mission impact. Red-team prompt injection and marking propagation.
6. Require independent steward and security approval, sign the artifact, and
   use deterministic compartment-safe A/B cohorts.
7. Apollo canaries the candidate. Drift or regression immediately restores the
   last known-good digest and seals proposal, evals, approvals, deployment, and
   rollback into the audit ledger.

## Full-Stack Implementation

- **Web UI:** Next.js control posture, evidence timeline, requirement matrix,
  vendor queue, finding ownership, approvals, and audit views.
- **Gateway:** FastAPI with OIDC/WebAuthn, request signing, idempotency, quotas,
  purpose binding, and policy enforcement.
- **Streaming:** Kafka-compatible topics keyed by `tenant_id:mission_id`, schema
  registry, bounded retries, backpressure, and dead-letter quarantine.
- **Data:** Foundry datasets and Ontology; encrypted object storage for original
  evidence; PostgreSQL-compatible transactional approval state.
- **Retrieval:** marking-aware lexical/graph/vector indexes containing only
  policy-visible chunks with lineage preserved.
- **Inference:** AIP model router selects an approved model by classification,
  task, latency, cost, residency, and eval status; deterministic rules remain
  authoritative for scoring and access.
- **Observability:** OpenTelemetry traces, SLOs, evaluation dashboards, drift
  alerts, immutable audit hashes, and sanitized structured logs.

Representative event subjects are `evidence.collected.v1`,
`control.evaluated.v1`, `vendor.deteriorated.v1`, `finding.opened.v1`, and
`bundle.requested.v1`. Consumers require event ID, idempotency key, schema
version, producer identity, trace ID, timestamp, content digest, and signature.

## Security and Governance

Authorization combines RBAC, ABAC, relationship-based access, purpose, mission,
classification, compartment, and coalition release constraints. Enforcement is
repeated at gateway, service, Ontology action, search, model tool, and storage.
All workloads use mTLS identities, least-privilege egress, signed images,
tenant-scoped KMS keys, short-lived credentials, replay protection, and default
deny. Missing policy, identity, telemetry, or key services moves AEGIS Federal
to read-only safe mode.

Prompt, model, workflow, catalogue, and policy registries are independently
versioned. Logs are hash-chained and exported to immutable storage. Raw secrets,
credentials, and protected payloads never enter prompts or telemetry. Counsel
owns regulatory interpretation; control owners own evidence; model stewards own
eval fitness; Apollo release owners own promotion and rollback.

## Code Examples

```python
report = evaluate_assurance(
    tenant_id=principal.tenant_id,
    mission_id=principal.mission_id,
    requirements=counsel_approved_catalogue,
    controls=ontology_controls,
    evidence=policy_filtered_evidence,
    framework_versions={Framework.CCSPA: "counsel-map-2026.1"},
)

bundle = prepare_evidence_bundle(request, report, counsel_approved_catalogue)
if not bundle.export_allowed:
    raise PolicyDenied("two distinct approvers are required")
```

The report hash covers the framework versions, effective time, control results,
findings, and coverage. This supports exact replay while keeping probabilistic
model output outside the compliance decision path.

## Scenario Walkthrough

At 02:14Z an Azure connector emits a signed IAM configuration observation. The
ingress verifies workload identity, signature, replay window, tenant, and schema;
Foundry normalizes it into temporal `Evidence` and links it to the critical IAM
control. AIP triage correlates an EDR event and an identity change, citing three
authorized evidence handles. Gotham opens a finding because one critical system
lacks current incident-response evidence.

The recommendation agent drafts a remediation package with owner, due date,
affected systems, confidence, and rollback plan. Policy classifies it as high
risk. An operator corrects a mistaken service-account relationship; the package
is recomputed, and two distinct authorities approve the sanitized action. The
execution service re-authorizes immediately before dispatch and records outcome,
artifacts, and hashes.

Offline, that correction joins the exact resolver and prompt versions. A bounded
candidate adds a service-account disambiguation step. Holdout evaluation shows
higher precision without violating recall, leakage, or latency floors. A model
steward and security reviewer approve a 5% Apollo canary. The candidate promotes
only after the observation window passes; otherwise Apollo restores the prior
signed artifact. Artemis learns from the outcome without changing its goals,
authority, or safety constraints.
