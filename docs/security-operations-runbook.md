# Security, privacy, release, incident, and deployment runbook

This is an engineering control plan, not legal advice or a certification. ClearGlassInc Artemis operators must replace every placeholder and validate external controls.

## Production architecture and environment

The FastAPI service requires `CONTROL_PLANE_API_KEY` (temporary bootstrap only; migrate to OIDC), `CONTROL_PLANE_DATABASE_URL`, `CONTROL_PLANE_ALLOWED_ORIGINS`, `CONTROL_PLANE_ENVIRONMENT=production`, `CONTROL_PLANE_RATE_LIMIT_REQUESTS`, and `CONTROL_PLANE_RATE_LIMIT_WINDOW_SECONDS`. Protected-asset integrations must obtain a distinct 32-byte-or-longer signing key from KMS/HSM as `ARTEMIS_ASSET_SIGNING_KEY`; never reuse the API credential. Do not expose it to `NEXT_PUBLIC_*` variables.

At the edge: terminate TLS 1.2+, redirect HTTP, preserve the original client address only from trusted proxies, apply shared-store identity/tenant/IP quotas, managed OWASP WAF rules, bot challenges after behavioral thresholds, request-size limits, and reversible allow rules for verified search engines and accessibility tools. Stage HSTS without `preload`; add preload only after every subdomain owner accepts the permanence. API/session cookies, if introduced, must be `Secure`, `HttpOnly`, narrowly scoped, and `SameSite=Lax` or `Strict`; state-changing cookie-authenticated requests require synchronizer or signed double-submit CSRF tokens plus Origin checks. Rotate the session identifier after authentication, privilege changes, and recovery.

## Protected content and anti-extraction

Authorize the principal, tenant, clearance, compartment, purpose, tier, and asset on the server before issuing an asset grant. Use `ProtectedAssetSigner` with a KMS-provided key, an account-bound audience, at most 15-minute TTL, single-use/replay state for high-value downloads, `Cache-Control: private, no-store`, and `Content-Disposition`. Render `watermark_label` diagonally and subtly into every page/image/PDF on the server; keep a release/asset ID in metadata. Blur preview content only before authorization. Never embed protected originals, signing keys, proprietary prompts/logic, or source records in HTML or JavaScript.

A public page cannot prevent screenshots, photography, copying, or determined extraction. Watermarks and expiring access are deterrence and attribution aids, not impossible DRM. Do not block right-click, selection, keyboards, screen readers, or accessibility automation.

Progressive extraction response: record privacy-minimized event → throttle → proportionate accessible challenge → short block → analyst alert. Detect per-account concurrency, sequential enumeration, failed-token replay, burst downloads, and quota evasion. Never fingerprint invasively by default and never hack back, damage devices, or retaliate.

## Data lifecycle

Owners must complete a data inventory and records-of-processing assessment. Default proposal pending counsel/owner approval: raw request/security events 90 days; elevated incident evidence 365 days; approval/audit decisions 7 years only if a documented legal/contractual need exists; rejected AI drafts and detailed feedback 30 days; account data for contract term plus 30 days; encrypted backups 35 days. Minimize immutable logs because deletion is intentionally difficult. Store pseudonymous IDs, action, object, decision, policy version, timestamp, correlation ID, and integrity seal—not bodies, tokens, URL queries, credentials, free-text PII, or protected content. Legal holds are documented, scoped, reviewed, and released. Deletion jobs must cover primary data, derived indexes, model/eval corpora, caches, and backup expiry, then create a non-sensitive completion receipt.

## Incident response

1. **Declare and preserve:** incident commander assigns severity; record UTC times; preserve read-only logs, affected hashes, deployment manifests, approvals, and chain of custody. Do not investigate from compromised hosts.
2. **Contain:** disable affected routes/accounts, revoke sessions and asset grants, rotate credentials through KMS, narrow WAF rules, and isolate deployments. Never destroy attacker systems or hack back.
3. **Assess:** determine data/types/subjects/tenants/jurisdictions, timeline, access/exfiltration evidence, and safety impact. Counsel determines regulator, customer, insurer, law-enforcement, and data-subject notification duties and deadlines.
4. **Eradicate/recover:** patch from reviewed source, rotate the full trust chain, restore into isolation, verify hashes and migrations, canary, monitor, and obtain incident-commander approval.
5. **Learn:** preserve a blameless record, add tests/evals, track actions, and delete incident data when holds expire.

Alert starting points requiring tuning: any admin MFA bypass/recovery; 5 failed credentials per account/10 minutes; 20 grant failures per account/5 minutes; 3 concurrent regions per account; >2× baseline downloads; audit-chain verification failure; production default-secret rejection; new critical dependency finding. Page a human for critical integrity, admin, or confirmed exfiltration events.

## Backups, keys, and restore

Use envelope encryption with KMS/HSM, separate production/backup principals, immutable versioned backup storage, quarterly key rotation (immediate on exposure), and dual control for root recovery. Monthly restore tests must validate a clean environment, schema, sample record counts, authorization, audit-chain integrity, and RPO/RTO; quarterly exercises include a revoked-key and regional-loss scenario. Record outcomes without secrets.

## Release provenance, deployment, verification, rollback

1. From a clean protected branch run tests/scans and `python security/release_manifest.py --output SHA256SUMS`.
2. Review `git diff`, SBOM/dependency results, migrations, and the manifest. Sign the commit/tag and manifest in the approved CI identity (Sigstore or organizational signing key); the local hash alone is not identity proof.
3. Build with production settings; reject `.env`, keys, source maps, coverage, test fixtures, internal notes, unpublished content, database files, and VCS metadata. Deploy the exact digest through Apollo/hosting canary controls.
4. Verify HTTPS redirect, certificate, headers/CSP, canonical URLs, `/legal`, `/.well-known/security.txt`, API auth failures, rate limiting, tenant denial tests, logs without secrets, WAF accessibility/search paths, metrics, and a protected download expiry/watermark.
5. Promote only with named owner approval. Monitor error, latency, auth denial, scraping, and CSP signals.

Rollback: stop promotion; route traffic to the last signed artifact digest; run only a tested backward migration (otherwise forward-fix); revoke newly issued grants/keys if trust changed; clear CDN content without deleting evidence; verify health, authorization, and audit seals; document decision and impact. Database rollback requires a pre-deploy snapshot and explicit data-owner approval.

## Residual risk and external actions

Repository code cannot establish MFA/SSO, distributed replay prevention, entity-level Palantir policy, WAF/CDN/DNS, TLS, SIEM paging, KMS/HSM, encrypted immutable backups, DAST against a deployed target, signed releases, consent-vendor configuration, or legal validity. Hosting/security owners must implement and evidence those controls. Counsel must approve privacy bases/notices, cookie behavior, retention, accessibility obligations, licensing restrictions, takedown handling, cross-border transfers, children rules, and incident notices. An accessibility specialist must perform WCAG 2.2 AA manual keyboard/screen-reader/contrast review. Independent penetration testing is required before mission-sensitive use.
