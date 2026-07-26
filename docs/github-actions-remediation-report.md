# GitHub Actions Remediation Report

**Repository:** ClearGlassInc Artemis

**Audit date:** 2026-07-26
**Scope:** Every file in `.github/workflows/`

## Executive decision

The repository contains six workflows. The audit found no plaintext credentials and
no workflow that executes fork-controlled code with a write-capable token. Three
workflows were already appropriately pinned and permissioned. Three required
immediate hardening: Browser Intelligence CI and Stripe Security used mutable action
tags and persisted the checkout token, while Pages packaged the complete repository
instead of a site-only allowlist.

After remediation, five workflows are **valid and ready**. Azure Functions is
**valid but needs improvement/configuration** and must remain unexecuted until the
production environment, OIDC variables, package location, smoke test, and rollback
procedure are confirmed by a repository administrator.

## Workflow inventory and dependency map

| Workflow | Trigger | Effective permissions | Secrets / variables | Jobs and dependencies | Cache / artifact | Environment / target | Final status |
|---|---|---|---|---|---|---|---|
| `azure-functions-python.yml` | Push to `main` for Function paths; manual | Default none; validation `contents: read`; deploy adds `id-token: write` | Repository variables for app name, package path, and Azure OIDC identity; no secrets | `validate` detects configuration; conditional `deploy` needs validation | Python package is assembled in-place; no cross-job artifact | Protected `production`; Azure Function App named by variable | **Valid but needs improvement/configuration** |
| `browser-intelligence-ci.yml` | Relevant pushes/PRs; manual | `contents: read` | None | Independent Python test and Next.js build jobs | pip/npm caches; lockfile-backed npm install; no artifact | None | **Valid and ready** |
| `financial-watchdog-ci.yml` | Relevant pushes/PRs; manual | `contents: read` | None | Four-version Python matrix compiles, lints, tests, and validates CLI | pip cache; no artifact | None | **Valid and ready** |
| `pages.yml` | Relevant pushes to `main`; manual | Default none; build `contents: read`; deploy only `pages: write`, `id-token: write` | GitHub OIDC only; no repository secret | `build` validates and stages; `deploy` requires successful build | Official Pages artifact containing only `_site` | `github-pages`; GitHub Pages | **Valid and ready** |
| `stripe-security.yml` | Pushes to `main`/`master`; PRs; manual | `contents: read` | None; scans for Stripe secret formats without printing configured secrets | One credential scanning job | None | None | **Valid and ready** |
| `supply-chain-guard.yml` | Relevant pushes/PRs; Mondays 05:17 UTC; manual | `contents: read`, `security-events: write`; API job narrows to contents only | A non-production CI-only API key and SQLite URL | Independent policy scan/SARIF upload and API migration/lint/test jobs | setup-python pip cache; SARIF uploaded to code scanning | None | **Valid and ready** |

## Findings and exact remediation

### 1. Browser Intelligence CI — repaired

**Failure risks:** mutable `@v4`/`@v5` action references allowed upstream tag drift;
checkout credentials remained in the worktree; `ubuntu-latest` could change without
review; `npm install` was nondeterministic; the cache pointed at `package.json`
instead of a lockfile; and unrestricted triggers wasted capacity.

**Patch:** pin checkout, Python, and Node setup actions to reviewed commit SHAs;
disable persisted credentials; fix the runner to Ubuntu 24.04; add least-privilege
permissions, concurrency cancellation, timeouts, names, relevant path filters, and
manual dispatch; commit `apps/web/package-lock.json`; use `npm ci --ignore-scripts`;
and retain fail-fast shell/test behavior. The complete corrected definition is the
checked-in `.github/workflows/browser-intelligence-ci.yml`.

### 2. GitHub Pages — repaired

**Failure risk:** uploading `path: "."` placed source, policy, documentation, and
other repository content in the deployment artifact. Build validation and deployment
also shared a single write-capable job, contrary to separation-of-duties guidance.

**Patch:** split `build` and `deploy`; make deployment depend on the successful
build; stage only `index.html`, optional `.nojekyll`, and optional `assets/`; assert
that the entrypoint is non-empty before upload; upload `_site` with the official
Pages artifact action; and grant Pages/OIDC write permissions only to deployment.
The complete corrected definition is `.github/workflows/pages.yml`.

**Rollback:** rerun this workflow at the last known-good commit (or revert the site
commit and merge); the immutable artifact for that run is then deployed through the
same gated job. Protect the `github-pages` environment if approval is required.

### 3. Stripe Security — repaired

**Failure risks:** mutable checkout reference, persisted credentials, floating runner,
no timeout/concurrency control, and an unnecessary hardcoded Stripe account identifier
in logs. The identifier was not a secret, but it provided no validation value.

**Patch:** pin checkout by SHA, disable persisted credentials, fix the runner, add a
timeout and concurrency group, improve error annotation, and replace the account log
with a credential-free security contract. The complete corrected definition is
`.github/workflows/stripe-security.yml`.

### 4. Azure Functions — execution blocked pending production facts

The YAML and OIDC design are structurally safe: the validation job cannot mint an
Azure token and the deploy job runs only after detection succeeds. However, no
Function package exists in this revision, repository variables cannot be verified
locally, and no post-deployment health check or Azure slot-swap rollback is defined.

**Required governance before execution:**

1. Confirm `AZURE_FUNCTIONAPP_PACKAGE_PATH` contains `host.json` and locked Python
   dependencies.
2. Configure `AZURE_FUNCTIONAPP_NAME`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and
   `AZURE_SUBSCRIPTION_ID` as repository/environment variables, never plaintext.
3. Restrict the federated identity subject to this repository and the `production`
   environment; add required reviewers to that environment.
4. Add an authenticated health check and prefer deployment to a staging slot followed
   by an approved slot swap. Document the swap-back command and retention window.
5. Change missing manual-dispatch configuration from a skip to a hard failure once
   the application package is introduced, preventing false-green production runs.

Until these controls exist, do not manually dispatch this workflow. Its push trigger
is dormant for application code because the referenced Function paths are absent.

### 5. Financial Watchdog CI — no patch required

Actions are SHA-pinned, credentials are not persisted, permissions are read-only,
dependency caching is scoped to the package manifest, the matrix is bounded, and
compile/lint/test/coverage/CLI gates are explicit. Provider extras may resolve newer
transitive dependencies over time; schedule a lock/constraints-file improvement, but
this is not an immediate correctness defect.

### 6. Supply Chain Guard — no patch required

Actions are SHA-pinned, the scanner is dependency-free, SARIF upload is observable,
and the API validation job explicitly narrows permissions. The CI API key is an
obvious non-production test value rather than a credential. `continue-on-error` is
limited to SARIF publication so a permissions limitation cannot hide the policy
scanner's own exit status.

## Fix and rollout order

1. Merge the pinning/token hardening for Browser and Stripe.
2. Merge the deterministic web lockfile and verify both Browser jobs.
3. Merge the Pages artifact allowlist and build/deploy separation.
4. Run Supply Chain Guard against the final workflow set and review both JSON/SARIF.
5. Run non-deployment CI workflows manually or through a pull request.
6. Deploy Pages only after environment policy review and inspection of `_site`.
7. Keep Azure blocked until all five production prerequisites above are evidenced.

## Validation and rollout runbook

### Pre-merge

1. Parse every YAML file with both a YAML parser and `actionlint` (GitHub expression
   and workflow-schema validation).
2. Run `python3 security/ci_guard.py` and require zero high/critical findings; review
   medium/low findings rather than suppressing them.
3. Run the exact Python suites and production web build used by CI.
4. Run `npm ci --ignore-scripts` from a clean tree to prove lockfile reproducibility.
5. Inspect `_site` with `find`; it must contain only the public entrypoint and approved
   static assets. Search it for credential patterns before deployment.

### Approved execution

Safe CI workflows are Browser Intelligence CI, Financial Watchdog CI, Stripe Security,
and Supply Chain Guard. They may run on pull requests because they expose no secrets
and have no deployment capability. Pages is approved only after inspecting its staged
artifact and confirming the `github-pages` environment. Azure is not approved.

GitHub-hosted execution requires a configured remote and authenticated GitHub access.
If either is absent, run local equivalents, record results in the pull request, and
allow normal pull-request triggers to execute the hosted jobs. Never add credentials
to make a local environment resemble GitHub Actions.

### Monitoring after deployment

- Confirm the Pages deployment URL and HTTP status, content hash, artifact/run IDs,
  source commit, environment approval actor, and deployment duration.
- Alert on cancelled/failed deployment jobs, unexpected manual dispatches, permission
  changes, artifact growth, or a deployed source SHA that differs from the approved SHA.
- For future Azure deployment, monitor Function health, error/latency rates, cold
  starts, slot state, and OIDC sign-in audit records; automatically stop promotion on
  smoke-test failure.

### Weekly health checks

- Keep the existing Monday Supply Chain Guard schedule.
- Review pinned action releases and Dependabot PRs; update SHAs only through reviewed
  changes with release-note verification.
- Audit workflow permissions, environment reviewers, OIDC trust subjects, stale
  secrets/variables, runner images, artifact retention, and cache hit/anomaly data.
- Exercise a non-production rollback quarterly and verify that known-good Pages and
  Azure artifacts remain reproducible.
- Review flaky-job rate, queue/run duration, dependency advisories, SARIF ingestion,
  and branch-protection required-check alignment.

## Audit boundary

No workflow was dispatched during remediation. Deployment safety gates cannot be
fully confirmed from a checkout without GitHub environment settings, repository
variables, hosted logs, or credentials. This report deliberately treats those facts
as unknown rather than assuming production access exists.
