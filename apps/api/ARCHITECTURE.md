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
│   │   └── domain.py          # compatibility exports
│   ├── schemas/
│   │   ├── product.py
│   │   ├── approval.py
│   │   ├── event.py
│   │   ├── order.py
│   │   ├── inventory.py
│   │   └── domain.py          # compatibility exports
│   ├── crud/
│   │   ├── product.py
│   │   ├── approval.py
│   │   ├── event.py
│   │   ├── order.py
│   │   └── inventory.py
│   ├── services/
│   │   ├── product_service.py
│   │   ├── approval_service.py
│   │   ├── audit_service.py
│   │   └── control_plane.py   # compatibility exports
│   └── api/
│       ├── dependencies.py
│       ├── routes.py          # compatibility router export
│       └── route_handlers/
│           ├── health.py
│           ├── products.py
│           ├── approvals.py
│           ├── events.py
│           └── inventory.py
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

No payment, refund, fulfillment, or order-execution endpoint is enabled by this migration.
