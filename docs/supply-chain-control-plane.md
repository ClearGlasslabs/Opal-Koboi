# Artemis Supply-Chain and Commerce Control Plane

This system treats CI/CD and business mutations as privileged control-plane operations.

## CI/CD controls

- Scans every workflow on pull requests, pushes to `main`, weekly schedules, and manual runs.
- Fails on dangerous `pull_request_target`, untrusted checkout, write permissions on low-trust events,
  OIDC on low-trust events, mutable action tags, direct event-to-shell interpolation, self-hosted
  runner exposure, unverified workflow artifacts, and `write-all`.
- Requires full 40-character action commit pins.
- Produces JSON, Markdown, and SARIF output.
- Uses no third-party parser or package during the security gate.

## API controls

- Pydantic v2 settings through `pydantic-settings`.
- SQLAlchemy 2 typed models and Alembic-managed schema. Application startup never calls `create_all()`.
- Decimal-backed prices (`NUMERIC(18,2)`), nonnegative database constraints, optimistic versions,
  idempotent request identifiers, API-key authentication, and rollback-safe sessions.
- High-risk price or inventory changes require a second independent approver.
- Audit events are chained with SHA-256 hashes to make deletion or modification detectable.

## Deployment sequence

```bash
cd apps/api
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For Azure deployment, configure GitHub OIDC federation and repository variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, and
`AZURE_FUNCTIONAPP_NAME`. Do not restore a publish-profile secret.
