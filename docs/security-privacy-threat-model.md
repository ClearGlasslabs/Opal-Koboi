# ClearGlassInc Artemis security, privacy, and IP threat model

**Status:** engineering assessment, 2026-08-03. **Not legal advice, a certification, or a claim of compliance.** Counsel must determine which laws apply from the operator, user, data-subject, customer, and hosting locations.

## Scope and assumptions

This assessment covers the tracked static pages, Next.js application, FastAPI control plane, SQLite/PostgreSQL persistence, Python intelligence modules, GitHub Actions, and documented GitHub Pages/Apollo-style deployments. The public UI contains demonstrative mission data; it is not an authorization boundary. Production identity, MFA, KMS/HSM, WAF/CDN, SIEM, backup, and Palantir controls are external dependencies and were not observable in this repository.

## Prioritized risks

| Rank | Risk | Likelihood / impact | Existing evidence | Required treatment |
|---:|---|---|---|---|
| P0 | Shared static API key permits impersonation, has no identity/role/tenant context, rotation, session binding, or MFA | High / Critical | `X-Control-Plane-Key` protects all non-health API routes | Replace at the gateway with OIDC/OAuth 2.1, phishing-resistant admin MFA, short-lived audience-bound tokens, RBAC/ABAC and tenant/entity policy. Until then fail closed in production, rate-limit, rotate, and never log credentials. |
| P0 | Sensitive or coalition data could be published in a client bundle or public static page | Medium / Critical | UI renders illustrative `SECRET // COALITION` content client-side | Treat the UI as public demonstration only. Authorize every record server-side, filter at entity/row/column level, and never serialize protected prompts, source data, keys, algorithms, or unpublished content to the client. |
| P0 | No deployed edge proof for HTTPS redirect, WAF, DDoS/bot controls, or HSTS preload safety | Medium / Critical | Repository can configure response headers but not DNS/edge | Hosting owner must enforce TLS 1.2+, redirect HTTP, stage HSTS before preload, configure managed WAF/bot rules and accessibility/search-engine allow paths, and retain reversible rules. |
| P1 | Bulk extraction, enumeration, credential stuffing, and token replay | High / High | Bounded list parameters exist, but no distributed quotas or anomaly response | Apply identity+tenant+IP quotas in a shared store and progressive log → throttle → challenge → temporary block → alert. Bind tokens to audience/issuer/nonce; do not use invasive fingerprinting by default. |
| P1 | XSS/clickjacking/data exfiltration through weak CSP | Medium / High | Next.js CSP allowed `unsafe-inline`; API headers omitted CSP and cross-origin isolation policies | Generate a per-request nonce, restrict origins, deny framing, set strict cross-origin/resource policies, and test headers. Keep CSP reporting privacy-preserving. |
| P1 | Privacy overcollection or indefinite retention in events, audit, analytics, errors, and feedback | Medium / High | Request metadata and domain/audit events persist; no executable deletion schedule | Minimize fields, pseudonymize identifiers, prohibit bodies/tokens/PII in telemetry, document schedules, implement verified deletion/legal hold workflows, and restrict immutable audit content to necessary metadata. |
| P1 | CI/release artifact or dependency compromise | Medium / High | Some actions are SHA-pinned; dependency ranges and invalid Dependabot ecosystem remain | Add secret, SAST, dependency, and artifact checks; lock dependencies; produce SHA-256 manifests; sign releases in the deployment environment; block source maps/dev files/secrets. |
| P1 | Upload/webhook/recovery/admin paths could be added without hardened patterns | Medium / High | These paths are not currently implemented | Require raw-body webhook signatures, replay windows/idempotency, MIME+magic-byte validation and isolated scanning, step-up MFA, recovery alerts, and authorization tests before exposing them. |
| P2 | Copying, screenshots, model training, resale, or provenance loss | High / Medium | Public content is necessarily retrievable; ownership metadata is incomplete | Add notices, canonical/structured provenance and lawful license terms. For authorized premium responses use user/time watermarks, `no-store`, and expiring signed access. These deter misuse but cannot prevent screenshots, photography, or determined extraction. |
| P2 | Availability loss or unsafe autonomous change | Medium / High | Approval concepts exist; runtime services and backups are external | Enforce two-person gates for consequential actions, signed versioned changes, canaries, kill switches, tested restore/rollback, immutable evidence, and no destructive retaliation or hacking back. |

## Trust boundaries and abuse cases

1. **Browser → edge/API:** hostile input, CSRF, XSS, forged headers, replay, scraping, oversized payloads.
2. **API → database/event bus/model tools:** injection, confused deputy, tenant leakage, prompt injection, excessive tool authority. SQLAlchemy parameterization reduces SQL injection risk; policy checks must still precede queries and writes.
3. **Operator/administrator → control plane:** stolen sessions, insider misuse, account sharing, unsafe recovery, unreviewed model or prompt changes.
4. **CI → registry/runtime:** poisoned dependency, leaked secret, unsigned artifact, source-map/dev-file publication, rollback tampering.
5. **Coalition/Palantir boundaries:** classification downgrade, purpose/compartment mismatch, lineage loss, disallowed model routing.

## Privacy and legal issue-spotting for counsel

Depending on facts and jurisdiction, review PIPEDA and applicable Canadian provincial private-sector laws; Québec Law 25; GDPR/UK GDPR and ePrivacy/PECR; US state privacy and breach laws (including California CPRA); COPPA/age-design duties; consumer-protection and automatic-renewal rules; CASL and similar marketing laws; PCI DSS contractual scope if payment data is introduced; copyright/database rights, DMCA/Canadian notice procedures, contract enforceability, open-source licenses, sanctions/export controls, records/public-sector requirements, and WCAG 2.2 AA / AODA / ADA or equivalent accessibility duties. Consent is not always the correct legal basis. Essential storage must be distinguished from optional analytics/advertising, which must remain off until valid consent where required.

## Acceptance criteria

- No production start with a repository default credential; no secret/body/query-string logging.
- Server-side authorization and tenant/compartment filtering precede protected reads and writes.
- Nonce-based CSP and baseline headers are present; sensitive responses use `no-store`.
- Legal templates are visibly linked but are not published as final until placeholders are completed and counsel approves them.
- CI scans code, dependencies, secrets, and release artifacts; SHA-256 provenance is reproducible.
- Incident procedures preserve evidence, revoke keys, notify through counsel, restore cleanly, and expressly prohibit hacking back.
