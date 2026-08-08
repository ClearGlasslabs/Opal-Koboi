# Product system dependency map

## Discovery baseline

Repository inspection found one authoritative public product narrative: `CG-os.html` describes **CG-OS Artemis** and links to contact, while `index.html` links to that flagship page. The FastAPI `products` table is a separately authenticated operational inventory/control-plane model with mutable prices and stock; it is not treated as public merchandising data. No Stripe product or price identifier is present in application product data.

## Runtime map

`lib/products/source.ts` (public source) → `domain.ts` (Zod normalization) → `registry.ts` (validation and deterministic registry) → `query.ts` (selectors/ranking/facets) → `/products` catalog and `/products/[slug]` detail → state-aware CTA resolver (details/contact or an authoritative checkout URL only) → typed browser event contract → generated route metadata, JSON-LD, and sitemap → Next standalone build/deployment.

Malformed records are reported individually and excluded from the public projection without taking down valid records. Duplicate IDs, slugs, SKUs, Stripe Price IDs, and orphan relationships are surfaced as registry issues rather than silently overwritten.
