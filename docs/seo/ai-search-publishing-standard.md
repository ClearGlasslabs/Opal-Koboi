# ClearGlass AI Search & Evidence Publishing Standard

Use this standard for every indexable service page, product page, comparison, technical briefing, article, assessment, and research asset.

## 1. Search identity

- One canonical production URL per intent.
- One primary search intent per page.
- Do not create near-duplicate city, industry, or keyword variants.
- Preview, staging, experiment, and internal application URLs must not compete with production URLs.
- Use the approved company and product names consistently.

## 2. Direct-answer structure

Within the first meaningful content block, answer the page's primary question in 40–90 words using plain factual language. Then expand with evidence, procedures, examples, tables, limitations, FAQs, and implementation detail.

Recommended order:

1. Direct answer / definition
2. Who the page is for
3. Problem and decision criteria
4. ClearGlass approach or product scope
5. Architecture / process / controls
6. Evidence or worked example
7. Limitations and non-goals
8. FAQ
9. CTA
10. References / methodology / update history where appropriate

Do not distort prose into unnatural “AI chunks.” Write for people first while keeping facts and headings explicit.

## 3. Claim classes

Every material claim must be classified before publication:

| Class | Example | Publication requirement |
|---|---|---|
| Verified company fact | Legal name, approved location | Evidence source and owner |
| Verified product fact | Capability, availability, integration | Product-owner approval |
| Technical fact | Protocol behavior, framework requirement | Primary/authoritative source |
| Quantitative claim | Module count, performance result | Reproducible source + date |
| Compliance statement | “aligned with”, “supports” | Exact control mapping or documented basis |
| Certification claim | ISO/SOC/etc. certified | Current certificate/report evidence; never infer |
| Customer result | Time/cost/risk improvement | Customer permission + measurement method |
| Analysis/inference | Architecture recommendation | Label as analysis; state assumptions |
| Opinion | Strategic recommendation | Attribute to author/reviewer |

If evidence is missing, remove the claim or mark the draft `REQUIRES CONFIRMATION`. Never “upgrade” readiness/alignment language into certification.

## 4. AI-answer visibility

Search and answer engines need accessible, high-quality source content more than gimmicks. Each important page should include, where useful:

- Explicit definition
- Concise summary
- Descriptive headings
- Real examples or reference architectures
- Tables with meaningful labels
- Step-by-step procedures
- Factual FAQs
- Limitations and failure modes
- Named author/reviewer
- Methodology
- References to authoritative primary sources
- Published and last-reviewed dates
- Change/update history for material revisions

Do not create fake citations, fake authors, fake experts, fake reviews, fake partners, or synthetic customer stories.

## 5. Schema policy

Structured data must match visible content and the real entity.

Allowed when valid:

- `Organization` — company homepage/entity information
- `WebSite` — canonical website
- `Service` — genuine service page
- `Product` — genuine product with visible product facts
- `SoftwareApplication` — only if the page and product satisfy the type
- `Article` — authored editorial content
- `BreadcrumbList` — visible breadcrumb trail
- `ContactPage` / `AboutPage` — corresponding page types
- `FAQPage` — only when the FAQ is visible and the schema use is appropriate; do not expect a Google rich result merely because it is present

Do not add review/rating markup without real eligible reviews. Do not use LocalBusiness unless the represented business/location satisfies the type and all location details are factual.

## 6. Product and partner references

When mentioning third-party products or platforms:

- Describe the relationship precisely.
- Do not imply partnership, certification, endorsement, integration status, customer status, or affiliation without evidence.
- Separate reference architecture language from deployed-production claims.
- Prefer “designed to integrate with” or “reference architecture using” only when technically true and approved.

## 7. Local SEO

A city page requires distinct, useful local content and a genuine service relationship to that market. It must not be a city-name substitution template.

Required evidence before a local-office claim:

- Real operating address or eligible location
- Correct contact information
- Consistent business identity
- Operational ability to serve the market

If ClearGlass serves a market remotely, use “serving organizations in…” rather than inventing a local office.

## 8. Editorial evidence block

For technical/security/AI governance content, use a visible block containing:

- Author
- Technical reviewer
- Published date
- Last reviewed date
- Scope
- Methodology
- Primary references
- Assumptions
- Limitations
- Change log, when materially updated

## 9. Internal linking

Every indexable page should have:

- At least one link to its parent topic/service hub
- At least one link to a deeper supporting resource where available
- At least one relevant conversion path
- Descriptive anchor text

Do not use repetitive exact-match anchors at scale.

## 10. Conversion instrumentation

Every commercial page must define:

- Primary CTA
- Secondary CTA
- Analytics event name
- Lead-source/UTM capture
- Success state
- Error state
- CRM handoff or qualified-lead definition where available

No dark patterns. Do not preselect consent or misrepresent scarcity, urgency, pricing, availability, results, or guarantees.

## 11. Content freshness

| Content | Review cadence |
|---|---|
| Product pages | Monthly or on release/status change |
| Commercial services | Quarterly |
| Security/compliance guidance | Quarterly and on material standard/regulatory change |
| AI platform/model-specific guidance | Quarterly or on material platform change |
| Research/data reports | Annual minimum; preserve original publication date |
| Evergreen definitions | 6–12 months |
| Contact/privacy/security pages | Quarterly route/policy check |

Do not change dates merely to make old content look new. Update the content materially and disclose meaningful revisions.

## 12. Publication gate

A production page passes only when all applicable checks are true:

- [ ] Canonical URL is approved and returns 200
- [ ] Intent is unique within the site
- [ ] Title and description are unique and accurate
- [ ] Exactly one clear H1
- [ ] Direct answer is near the top
- [ ] Material claims have evidence or explicit confirmation status
- [ ] Product/location/certification wording is approved
- [ ] Internal links point to canonical URLs
- [ ] External factual citations use authoritative sources
- [ ] Images have dimensions and appropriate alt text
- [ ] Structured data matches visible content
- [ ] Author/reviewer/update data is present where needed
- [ ] Limitations are disclosed where decision-critical
- [ ] Primary and secondary CTAs are instrumented
- [ ] Mobile rendering is usable
- [ ] No known broken links/redirect chains
- [ ] Sitemap inclusion is correct
- [ ] Index/noindex state is intentional
- [ ] Core Web Vitals are tested before/after material UI changes
