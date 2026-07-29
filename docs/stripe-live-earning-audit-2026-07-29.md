# ClearGlassInc Artemis Stripe Account Live & Earning Audit

**Audit date:** 2026-07-29 (UTC)  
**Scope:** repository evidence in `/workspace/Opal-Koboi`; no authenticated Stripe Dashboard or bank-statement access was available.  
**Result:** **0/22 PASS, 4/22 FAIL, 18/22 NEEDS VERIFICATION**

## Audit method and status rules

This is an evidence-based audit, not an assertion that inaccessible account settings are healthy. Stripe secrets must never be
committed or pasted into an audit. Dashboard-only and bank-only controls are therefore marked **NEEDS VERIFICATION** until an
authorized ClearGlassInc Artemis operator records redacted evidence. A repository control is marked **FAIL** only where the
repository positively shows that the production payment capability is absent.

Repository findings:

- The API order model explicitly has no payment or fulfillment execution path.
- The API architecture explicitly says no payment or refund endpoint is enabled.
- No Stripe SDK dependency, Checkout/PaymentIntent implementation, webhook handler, Stripe signature verification, live object
  identifiers, or Stripe error handling was found in tracked application code.
- CI scans tracked files for Stripe secret and webhook-signing-secret formats. This is a useful leak-prevention control, but it
  does not prove that deployed credentials are live, current, correctly scoped, or operational.

Store evidence in an access-controlled audit system. Record only masked values (for example, key prefix plus last four
characters and bank last four); never store `sk_live_`, `rk_live_`, or `whsec_` values in this repository.

## Phase 1 — Account is in live mode

### 1. Stripe Dashboard is in live mode

- **Status:** NEEDS VERIFICATION
- **Current value:** No authenticated Dashboard evidence available.
- **Action needed:** An authorized administrator must open the Stripe Dashboard, select the production account, confirm the
  workbench/data view is **Live**, and capture a timestamped screenshot that excludes customer data and secrets. If the view is
  test/sandbox, switch to live before performing the remaining checks.
- **Priority:** CRITICAL
- **Estimated time:** 2–5 minutes.

### 2. API keys in use are live keys

- **Status:** NEEDS VERIFICATION
- **Current value:** No Stripe credentials are committed (correct); deployed secret configuration is inaccessible. The CI
  scanner rejects committed `sk_`, `rk_`, and `whsec_` values, but does not validate the deployment secret store.
- **Action needed:** In live-mode Developers/API keys and the production secrets manager, compare masked fingerprints. Confirm
  the client publishable key begins `pk_live_` and the server key begins `sk_live_` (or an intentionally scoped `rk_live_`).
  Confirm that no production runtime variable contains `_test_`. Do not reveal full values in screenshots or logs.
- **Priority:** CRITICAL
- **Estimated time:** 10–20 minutes; 30–60 minutes if keys must be rotated and redeployed.

### 3. No restriction or pending-verification banner

- **Status:** NEEDS VERIFICATION
- **Current value:** Account capability/KYC state is unavailable.
- **Action needed:** Review all Dashboard warning banners and Settings/Business/Account status. Complete every outstanding
  identity, representative, ownership, tax, website, product, and bank verification request. Record the `charges_enabled` and
  `payouts_enabled` account capability results in the restricted audit record.
- **Priority:** CRITICAL
- **Estimated time:** 5 minutes to inspect; same day to several business days if Stripe must review documents.

## Phase 2 — Account can receive money

### 4. Bank account is linked and verified

- **Status:** NEEDS VERIFICATION
- **Current value:** No Dashboard or bank evidence available.
- **Action needed:** In payout settings, confirm the external account is verified and compare bank name, currency, routing-number
  suffix, and account-number last four against a current business-bank record. Complete microdeposit verification if offered.
- **Priority:** CRITICAL
- **Estimated time:** 5–10 minutes; 1–2 business days if microdeposits are required.

### 5. Payouts are enabled and scheduled

- **Status:** NEEDS VERIFICATION
- **Current value:** Payout enablement and schedule are unavailable.
- **Action needed:** Confirm payouts are neither paused nor disabled and `payouts_enabled` is true. Select daily or weekly based
  on treasury policy; weekly is recommended when reconciliation review is required. Resolve negative balances or compliance
  blocks before relying on the schedule.
- **Priority:** CRITICAL
- **Estimated time:** 5 minutes if enabled; same day to several business days if Stripe intervention is required.

### 6. Payout currency matches bank currency

- **Status:** NEEDS VERIFICATION
- **Current value:** Settlement and bank currencies are unavailable.
- **Action needed:** Compare the Stripe settlement currency with the external account currency and the bank's supported payout
  rail. Add an eligible same-currency account or explicitly document conversion fees and supported settlement behavior.
- **Priority:** HIGH
- **Estimated time:** 5–10 minutes; 1–3 business days to add/verify another account.

## Phase 3 — Payment processing is active

### 7. At least one payment method is enabled

- **Status:** NEEDS VERIFICATION
- **Current value:** Payment-method configuration is unavailable; no application payment flow exists in this repository.
- **Action needed:** Confirm Cards is enabled in live-mode payment-method settings and complete a production Checkout or
  PaymentIntent integration before accepting payments from this application. Enable ACH and wallet methods only where supported
  by the business country, currency, and Checkout configuration.
- **Priority:** CRITICAL
- **Estimated time:** 5 minutes for Dashboard configuration; 1–3 engineering days for a reviewed integration.

### 8. Business is not prohibited or unsupported

- **Status:** NEEDS VERIFICATION
- **Current value:** The repository describes defensive intelligence/research software, but the exact legal entity, products,
  jurisdictions, sales model, and merchant category supplied to Stripe are not auditable here.
- **Action needed:** Legal/compliance must map every actual product, customer type, jurisdiction, and funds flow to Stripe's
  current restricted-business policy at <https://stripe.com/legal/restricted-businesses>. Obtain written Stripe approval where
  required and retain it with the merchant-risk assessment. Do not infer eligibility from repository copy alone.
- **Priority:** CRITICAL
- **Estimated time:** 30–60 minutes for internal review; several business days for Stripe approval.

### 9. No unexpected holds or reserves

- **Status:** NEEDS VERIFICATION
- **Current value:** Balance, reserve, and pending-funds data are unavailable.
- **Action needed:** Review live Balance and each balance transaction. Separate ordinary pending settlement from reserve funds or
  holds; document expected settlement dates and contact Stripe Support about unexplained reserves.
- **Priority:** HIGH
- **Estimated time:** 10–20 minutes; support resolution varies from days to weeks.

## Phase 4 — Integration is live

### 10. Live webhook endpoint is registered and receiving events

- **Status:** FAIL
- **Current value:** No Stripe webhook endpoint or event handler exists in tracked application code; no authenticated Dashboard
  delivery evidence was available.
- **Action needed:** Implement a production HTTPS webhook endpoint, register it in live mode with only required event types,
  store its signing secret in the production secrets manager, and test a real/safe live lifecycle. Record delivery ID, event ID,
  HTTP 2xx result, latency, and idempotent processing result. Dashboard “send test event” alone does not prove a live charge flow.
- **Priority:** CRITICAL
- **Estimated time:** 4–8 engineering hours plus deployment review.

### 11. Webhook signature verification works

- **Status:** FAIL
- **Current value:** No Stripe SDK or `Stripe-Signature` verification code was found.
- **Action needed:** Verify every webhook against the exact raw request body, `Stripe-Signature` header, and endpoint secret
  before parsing or side effects. Reject missing, invalid, or stale signatures; deduplicate event IDs; log no secrets or payload
  PII. Add valid, tampered-body, wrong-secret, stale-timestamp, duplicate-event, and replay tests.
- **Priority:** CRITICAL
- **Estimated time:** 3–6 engineering hours.

### 12. Production uses no test-mode Stripe objects

- **Status:** NEEDS VERIFICATION
- **Current value:** No Stripe product, price, coupon, customer, or live-object configuration exists in this repository or its
  accessible environment.
- **Action needed:** Build a server-side allowlist of live Price IDs populated from the production secrets/configuration system.
  Inventory required products/prices/coupons in live mode, recreate test-only objects, and run a startup/deployment check that
  rejects test keys and non-approved IDs in production. Customer objects should be created or mapped in live mode.
- **Priority:** CRITICAL
- **Estimated time:** 1–4 hours, depending on catalog size.

### 13. Stripe error handling is complete

- **Status:** FAIL
- **Current value:** No payment code or handling for `card_error`, `api_error`, `invalid_request_error`, or
  `authentication_error` exists.
- **Action needed:** Add typed handling: show a safe decline/retry message for card errors; use bounded retry with idempotency for
  transient API failures; alert engineering on invalid requests; fail closed and page operations on authentication failures.
  Never expose Stripe exception bodies or sensitive decline details to clients. Cover each branch with tests.
- **Priority:** HIGH
- **Estimated time:** 4–8 engineering hours.

### 14. API version is pinned and reviewed

- **Status:** FAIL
- **Current value:** No Stripe dependency or explicit Stripe API version exists.
- **Action needed:** Select the current supported Stripe API version after reviewing its changelog, pin the SDK dependency, and
  set/version-test API requests and webhook endpoints consistently. Validate in a sandbox first, run contract tests, then use a
  canary deployment and rollback plan before upgrading production.
- **Priority:** HIGH
- **Estimated time:** 2–4 hours for initial setup; longer if migration changes are required.

## Phase 5 — Money is actually flowing

### 15. Successful live charges occurred in the last 30 days

- **Status:** NEEDS VERIFICATION
- **Current value:** No Stripe transaction access; no payment execution path in this repository.
- **Action needed:** Filter live Payments to successful transactions from 2026-06-29 through 2026-07-29 UTC. Verify at least one
  legitimate payment, its live indicator, currency, amount, customer/order reconciliation key, and balance transaction. A test
  or manually fabricated record does not qualify.
- **Priority:** CRITICAL
- **Estimated time:** 5–10 minutes after a payment exists; otherwise integration time plus settlement.

### 16. At least one payout reached the bank

- **Status:** NEEDS VERIFICATION
- **Current value:** No Stripe payout or bank-statement access.
- **Action needed:** Find a live payout with `Paid` status, open its reconciliation detail, and match its amount/date/reference to
  a posted credit on the business bank statement. Investigate differences using fees, refunds, disputes, and balance transactions.
- **Priority:** CRITICAL
- **Estimated time:** 10–20 minutes; first payout timing depends on account and country.

### 17. Dispute rate is below 1% and disputes are managed

- **Status:** NEEDS VERIFICATION
- **Current value:** Dispute counts, denominator, and open evidence deadlines are unavailable.
- **Action needed:** Calculate a documented 30-day and trailing-12-month dispute rate using consistent transaction/count rules;
  confirm each is below the business threshold of 1%. Submit factual evidence for every open dispute before its displayed
  deadline. Also monitor the card-network and Stripe program metrics shown in the Dashboard, which may use different windows.
- **Priority:** HIGH
- **Estimated time:** 15–30 minutes; 1–3 hours per evidence package.

### 18. Refund rate is below 5%

- **Status:** NEEDS VERIFICATION
- **Current value:** Refund counts/amounts and payment denominator are unavailable.
- **Action needed:** Compute both count-based and value-based refund rates for the last 30 and 90 days, excluding failed or
  canceled payments consistently. Confirm each is below the requested 5% internal threshold and investigate reasons, products,
  cohorts, and support patterns for any breach.
- **Priority:** MEDIUM
- **Estimated time:** 15–30 minutes; remediation depends on root cause.

## Phase 6 — Security and monitoring

### 19. Two-factor authentication is enabled

- **Status:** NEEDS VERIFICATION
- **Current value:** Team security settings are unavailable.
- **Action needed:** Require two-step authentication for every team member, preferring passkeys or hardware security keys and an
  authenticator app over SMS. Remove dormant users, verify least-privilege roles, and store recovery codes securely.
- **Priority:** HIGH
- **Estimated time:** 5–10 minutes per user.

### 20. Operational email notifications are enabled

- **Status:** NEEDS VERIFICATION
- **Current value:** Communication preferences and recipients are unavailable.
- **Action needed:** Enable and route payment, dispute, payout, and account/compliance warnings to monitored role addresses.
  Confirm escalation ownership and send/observe a safe notification test where Stripe supports it; do not rely on one mailbox.
- **Priority:** HIGH
- **Estimated time:** 10–20 minutes.

### 21. API keys have been rotated and are not stale

- **Status:** NEEDS VERIFICATION
- **Current value:** No key inventory, creation dates, access history, or rotation evidence is available. CI only prevents common
  credential formats from being committed.
- **Action needed:** Inventory live/restricted keys, owners, scopes, creation dates, and last-used metadata. Immediately rotate any
  key shared during development or stored outside the approved vault: create least-privilege replacement, deploy, verify traffic,
  expire old key, and monitor authentication errors. Establish a risk-based rotation policy and incident-triggered rotation.
- **Priority:** CRITICAL
- **Estimated time:** 30–90 minutes for a standard zero-downtime rotation.

### 22. Statement descriptor is correct

- **Status:** NEEDS VERIFICATION
- **Current value:** Statement descriptor is unavailable.
- **Action needed:** Set a Stripe-valid 5–22 character descriptor recognizable as ClearGlassInc Artemis or the customer-facing
  business name, then verify its preview and appearance with a legitimate low-value purchase/refund flow. Ensure support contact
  details are current to reduce disputes.
- **Priority:** HIGH
- **Estimated time:** 5–10 minutes plus card-statement posting time.

## Overall health and earning blockers

**Health score: 0/22 passed (0%).** This score reflects verified evidence, not a claim that all unverified controls are broken.
The account is **not audit-proven live or earning**. Four integration controls fail for this repository, and 18 account or
operational controls require authorized evidence.

### Critical blockers

1. Live-mode selection, production-key deployment, account verification, bank verification, and payout capability are unknown
   (items 1–5).
2. Payment-method/business eligibility and actual live revenue/payout evidence are unknown (items 7–8 and 15–16).
3. This repository has no live webhook receiver or signature verification (items 10–11).
4. Live Stripe object separation is unverified (item 12).
5. Key-rotation state is unknown (item 21).

If a different production service owns payments, items 10–14 must be re-audited against that service and its deployment; that
evidence would not make this repository a payment integration.

## Step-by-step remediation plan

1. **Assign owners and open a restricted evidence record (15 minutes).** Name one Stripe administrator, one finance reviewer,
   one security reviewer, and one payment-service engineer. Keep secrets, full bank details, and customer data out of tickets.
2. **Clear account-level earning blockers (30–60 minutes plus review time).** Verify items 1–8 in order: correct account/live
   mode, deployed key fingerprints, KYC/capabilities, bank, payouts, currency, cards, and business eligibility. Stop if any banner
   or capability disables charges or payouts.
3. **Implement the payment boundary (1–3 engineering days).** Use hosted Checkout or PaymentIntents, a server-side live Price-ID
   allowlist, idempotency keys, least-privilege server credentials, and no client access to secret keys.
4. **Implement and test webhooks (1 engineering day).** Complete items 10–11 with raw-body signature validation, minimal event
   subscriptions, deduplication, replay safety, asynchronous processing, metrics, and a dead-letter/reconciliation path.
5. **Add versioned error and object controls (0.5–1 engineering day).** Complete items 12–14; pin the SDK/API contract and add
   production startup guards plus unit/contract tests.
6. **Run a controlled live smoke transaction (30–60 minutes plus settlement).** With finance authorization, make a legitimate
   low-value purchase, confirm the successful Payment and webhook lifecycle, then issue a policy-approved refund if appropriate.
   Never use test card numbers in live mode.
7. **Prove settlement (first-payout window plus 15 minutes).** Reconcile the live balance transaction, Stripe payout, fees, and
   bank credit for item 16.
8. **Baseline risk and security (1–3 hours).** Calculate item 17–18 metrics, close evidence deadlines, enforce 2FA, configure
   notifications, rotate exposed/stale keys, and validate the descriptor (items 19–22).
9. **Independent sign-off (30 minutes).** Finance confirms bank/payout evidence, security confirms key/webhook/2FA controls, and
   the Stripe administrator confirms capabilities. Convert an item to PASS only when its dated evidence and reviewer are linked.

## Required evidence register

For each item, retain: audit timestamp, Stripe account ID in masked form, environment (live/test), reviewer, redacted screenshot
or exported object identifier, result, exception/waiver, remediation ticket, and expiry/recheck date. Suggested rechecks are daily
for capability/payout failures, monthly for operational metrics and team access, quarterly for keys/configuration, and after every
Stripe API or payment-service deployment.
