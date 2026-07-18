# ClearGlass Artemis Commerce Control Plane

## Architecture

The API is organized into explicit boundaries while preserving the original public imports and HTTP contract.

```text
apps/api/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── product.py
│   │   ├── approval.py
│   │   ├── event.py
│   │   ├── order.py
│   │   ├── inventory.py
│   │   ├── threat_model.py
│   │   └── domain.py          # compatibility exports
│   ├── schemas/
│   │   ├── product.py
│   │   ├── approval.py
│   │   ├── event.py
│   │   ├── order.py
│   │   ├── inventory.py
│   │   ├── threat_model.py
│   │   └── domain.py          # compatibility exports
│   ├── crud/
│   │   ├── product.py
│   │   ├── approval.py
│   │   ├── event.py
│   │   ├── order.py
│   │   ├── inventory.py
│   │   └── threat_model.py
│   ├── services/
│   │   ├── product_service.py
│   │   ├── approval_service.py
│   │   ├── audit_service.py
│   │   ├── threat_engine.py
│   │   ├── threat_model_service.py
│   │   └── control_plane.py   # compatibility exports
│   └── api/
│       ├── dependencies.py
│       ├── routes.py          # compatibility router export
│       └── route_handlers/
│           ├── health.py
│           ├── products.py
│           ├── approvals.py
│           ├── events.py
│           ├── inventory.py
│           └── threat_models.py
├── migrations/
├── tests/
├── requirements.txt
└── .env.example
```

## Boundary responsibilities

- **Models** define SQLAlchemy persistence contracts and database constraints.
- **Schemas** validate API and service inputs and serialize outputs.
- **CRUD** performs persistence operations without committing transactions.
- **Services** enforce idempotency, risk scoring, approvals, audit evidence, and business invariants.
- **Route handlers** translate authenticated HTTP requests into service calls.
- **Dependencies** own request-scoped database commit/rollback and API-key authorization.
- **Alembic** is the only production schema-management path. The application does not call `create_all()` at startup.

## Preserved security invariants

1. Money uses `Decimal` and `Numeric(18, 2)`, never binary floating point.
2. Product price and inventory cannot be negative.
3. Every mutation requires an idempotency request ID.
4. Optimistic version checks prevent lost updates.
5. High-risk price and inventory changes enter the approval queue.
6. The requester cannot approve their own consequential change.
7. Applied inventory changes create append-only inventory movement evidence.
8. Material actions create SHA-256 chained audit events.
9. Public clients can read the audit ledger but cannot manufacture audit events.
10. Orders are schema-only until payment and fulfillment services are implemented behind approval gates.
11. Production API documentation is disabled.
12. Database sessions roll back on failure and commit once per successful request.
13. Threat analysis is deterministic and does not execute attacks, tools, payloads, or production changes.
14. Every threat-analysis run records its architecture digest, rules digest, engine version, actor, and request identity.
15. Threat findings contain evidence and mitigations but never grant authority to act on a target system.

## Autonomous threat-modeling subsystem

The threat-modeling subsystem converts a typed architecture graph into reproducible findings at machine speed. It is intended for defensive architecture review, CI validation, critical-infrastructure assurance, agentic-system governance, and cyber-physical safety analysis.

### Inputs

A threat model contains:

- Components with trust zone, data classification, exposure, security controls, agent capabilities, memory, sensor, and actuation properties.
- Data flows with protocol, authentication, encryption, trust-boundary, and direction metadata.
- Explicit trust boundaries between zones.
- A canonical SHA-256 architecture digest.

### Deterministic analysis

`app/services/threat_engine.py` evaluates versioned rules across:

- STRIDE: spoofing, tampering, repudiation, information disclosure, denial of service, and elevation/tool abuse.
- Agentic AI: prompt injection, tool abuse, persistent-memory poisoning, and agent-to-agent collusion.
- Cyber-physical systems: sensor spoofing and actuator hijacking.
- Software supply chain: dependency and update-channel compromise.

The engine does not depend on an LLM. The same validated architecture and rule version produce the same ordered finding set. An LLM may later propose candidate architecture facts or mitigations, but those outputs must remain untrusted and pass through the typed validation and deterministic rule engine.

### Risk scoring

Each finding stores bounded 1-5 values for likelihood, impact, exposure, and control gap. The engine calculates a 0-100 score with consequence weighted most heavily, then exposure and control weakness. Findings are sorted by descending score with stable deterministic tie-breaking.

### Persistence and provenance

Migration `0003_autonomous_threat_modeling` adds:

- `threat_models`: versioned architecture snapshots and canonical digests.
- `threat_analysis_runs`: idempotent run identity, engine version, input digest, rules digest, finding count, and maximum risk.
- `threat_findings`: category, scenario, asset, component, trust boundary, scoring factors, evidence, and mitigation guidance.

Every create and analyze operation also appends a tamper-evident control-plane event. Analysis requires the expected model version and fails closed when the stored architecture no longer matches its digest.

### API surface

All routes remain under `/api/v1` and require the existing control-plane key:

- `POST /threat-models`
- `GET /threat-models`
- `GET /threat-models/{id}`
- `POST /threat-models/{id}/analyze`
- `GET /threat-models/{id}/runs`
- `GET /threat-models/{id}/findings`

The API creates models and evidence only. It does not perform scanning, exploitation, red-team execution, production remediation, or physical actuation.

## Why the pasted prototype was not copied literally

The requested separation was adopted, but weaker or outdated patterns were not introduced:

- `pydantic-settings` remains the settings provider for Pydantic v2.
- `psycopg` v3 remains the PostgreSQL driver.
- `Numeric`/`Decimal` remains the money representation instead of `Float`.
- Alembic remains mandatory; `Base.metadata.create_all()` is not executed by `main.py`.
- Approval endpoints remain database-backed and enforce four-eyes control.
- Audit events remain service-generated and hash-chained rather than accepting arbitrary public event creation.
- Existing module paths remain available through compatibility exports, so no caller is forced into an immediate migration.

## Migration sequence

```bash
cd apps/api
python -m pip install -r requirements-dev.txt
alembic upgrade head
ruff check app tests migrations
pytest -q
```

Migration `0002_orders_inventory` adds:

- `orders` with governed status, exact money, currency, versioning, and external-reference uniqueness.
- `inventory_movements` with immutable request identity, product linkage, actor, reason, signed delta, resulting inventory, and non-negative constraints.

Migration `0003_autonomous_threat_modeling` adds the architecture, analysis-run, and finding evidence stores described above.

No payment, refund, fulfillment, order-execution, offensive-testing, or autonomous-remediation endpoint is enabled by these migrations.
