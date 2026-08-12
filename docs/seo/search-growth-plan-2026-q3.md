# ClearGlass Inc. Search Growth Plan — Q3 2026

**Scope:** ClearGlassInc.com production search surface and the OPAL repository (`ClearGlasslabs/Opal-Koboi`).

**Objective:** Grow qualified branded, non-branded, local, commercial, industry, and answer-engine discovery and convert it into briefings, assessments, consultations, subscriptions, and business opportunities without manipulative SEO.

## Assumptions and missing information

1. The root static site is treated as the current OPAL production artifact because `.github/workflows/pages.yml` packages the root HTML, robots, sitemap, and assets and verifies the custom domain after deployment.
2. The Next.js application under `apps/web` is treated as a secondary application surface, not the canonical production website, until deployment ownership is explicitly changed.
3. No Google Search Console, Bing Webmaster Tools, GA4, CRM, backlink-platform, call-tracking, or revenue-attribution dataset was provided. Search volume, ranking difficulty, traffic, conversion, backlink, and AI-citation values in this plan are therefore **directional**, not measured account data.
4. No verified Lighthouse/PageSpeed or CrUX dataset was available in this audit. Core Web Vitals recommendations are code-level and standards-based until field/lab data is connected.
5. Burlington, Ontario is supported by the current public site. Toronto/Canada/United States may be treated as genuine service markets only where the public site supports them. **Do not claim a New York City office or local presence without evidence.** A service-area page may be used only if ClearGlass genuinely serves that market.
6. `CG-OS Artemis` is verified in OPAL's authoritative public product source. `ClearGlass AgentOps` and `BLUEDESK` are visible on the current live website. `Revenue Engine` is visible as a named capability/feature; do not publish it as a standalone product until product ownership, scope, pricing, and evidence are confirmed.
7. OPAL contains statements such as “SOC 2 / ISO 27001 ready.” These must not be transformed into certification claims without documentary evidence. Use precise language such as “designed to support” or “aligned with” only when substantiated.
8. No customer case-study outcomes, customer logos, certifications, awards, market-share statistics, or performance guarantees are assumed.
9. Full page briefs below cover the **highest-value canonical pages**. Supporting articles, comparisons, technical briefings, and tools use abbreviated briefs until promoted into the production queue.

---

# A. Executive findings

## Critical

### 1. Production search ownership is fragmented
OPAL contains a static production surface at repository root and a separate Next.js application whose metadata and sitemap point to the GitHub Pages project URL and describe “business productivity plans.” This creates a material risk of inconsistent brand, canonical, and query targeting if both surfaces become crawlable.

**Decision:** `https://www.clearglassinc.com/` is the canonical search identity. Any preview, GitHub Pages project path, test environment, or secondary app should either canonicalize to the production URL where equivalent or be excluded from indexing when it is not intended as public search content.

### 2. The production XML sitemap is severely under-scoped
The checked-in production sitemap contains only the homepage and `CG-os.html`. It does not represent a scalable content architecture for products, services, methodology, security, privacy, case studies, technical briefings, or future resources.

**Decision:** move to a generated or centrally maintained sitemap that includes only canonical, indexable, 200-status production pages.

### 3. Search positioning is too concentrated on Artemis / municipal intelligence
The OPAL homepage currently targets “AI intelligence,” “municipal cybersecurity,” OSINT, ontology, and agentic automation. ClearGlass's live public surface is broader: governed AI, AI automation, cybersecurity, agent systems, legal-tech/OSINT, and enterprise architecture.

**Decision:** make the homepage the company-level entity page, then give each commercial category one dedicated destination. Do not force every query into Artemis.

### 4. Claims require stronger evidence governance
The site contains quantitative module/API/camera counts and compliance-readiness statements. Search and AI systems reward clear, consistent entities and evidence; unsupported or stale claims create trust and reputational risk.

**Decision:** maintain a claim registry with owner, source, verification date, allowed wording, expiry/review date, and pages using the claim.

## High

### 5. Conversion paths are too weak for commercial search
“Request a briefing” is a valid high-intent CTA, but commercial pages should also provide a lower-friction assessment, checklist, or architecture review. Every high-intent page needs a measurable primary CTA and an alternative CTA.

### 6. AI-search readiness should come from evidence structure, not “AI SEO tricks”
Use direct answers, definitions, structured headings, verifiable facts, cited sources, methodology, limitations, authorship, update dates, and crawlable HTML. Do not create artificial answer-engine bait, fake expertise, or special markup that does not match visible content.

### 7. Homepage animation creates a performance risk
The starfield checks many star pairs on every animation frame. On larger displays this is an O(n²) rendering loop. Reduced-motion support is good, but performance should be bounded with a lower particle cap, spatial partitioning or line-density limits, pause-on-hidden behavior, and real CWV testing.

## Medium

- Replace legacy `meta keywords` emphasis with page-specific intent, entity clarity, internal linking, and content quality.
- Add complete Open Graph/Twitter metadata and a branded share image to every commercial page.
- Add breadcrumbs to every non-home canonical page and valid `BreadcrumbList` schema where the visible breadcrumb exists.
- Convert important Markdown-only technical documents into crawlable HTML editorial pages with canonical URLs, summaries, author/reviewer data, and update history.
- Add an editorial “last reviewed” workflow for security, AI governance, privacy, and compliance content.

---

# B. Branded search strategy

| Query family | Canonical destination | Purpose | Cannibalization rule |
|---|---|---|---|
| ClearGlass / ClearGlass Inc | `/` | Company/entity overview | Homepage owns company-level brand terms |
| ClearGlass products / platforms | `/products/` | Product index | Individual products target product names only |
| ClearGlass cybersecurity | `/services/cybersecurity/` | Cybersecurity capability | Homepage links to it; does not duplicate full service copy |
| ClearGlass AI / AI automation | `/services/ai-automation/` | AI automation capability | AgentOps page targets the product/entity, service page targets the service category |
| ClearGlass AgentOps | `/products/agentops/` | Product/capability page | One canonical product destination |
| ClearGlass BLUEDESK | `/products/bluedesk/` | Defensive operations product/capability | One canonical destination |
| ClearGlass Revenue Engine | `/products/revenue-engine/` **only after confirmation** | Product page if standalone product is approved | Until confirmed, keep it as an AgentOps capability section |
| ClearGlass OSINT / legal-tech OSINT | `/services/osint-automation/` | OSINT service/capability | Technical research articles support, not compete |
| ClearGlass methodology | `/methodology/` | How ClearGlass works, evidence, guardrails | Methodology facts are referenced, not copied wholesale |
| ClearGlass case studies | `/case-studies/` | Evidence hub | Publish only verified cases or anonymized technical briefings with explicit labels |
| ClearGlass security | `/security/` | Security posture and disclosure | Do not mix with generic cybersecurity consulting page |
| ClearGlass privacy | `/privacy/` | Privacy policy | Legal/compliance destination only |
| ClearGlass contact | `/contact/` | Contact / qualification flow | One canonical form destination |

### Brand entity consistency
Use **ClearGlass Inc.** as the legal/company entity when verified, and use product names exactly as approved. Avoid switching between “ClearGlassInc Artemis” and “ClearGlass Inc.” as if they are the same entity. Artemis should be presented as a product/platform family when that is the approved relationship.

---

# C. Keyword and intent map

Detailed execution mapping is maintained in `docs/seo/keyword-intent-map-2026-q3.csv`.

## Priority clusters

1. **Governed AI agents** — commercial/informational; executive, CTO, CIO, CISO, platform teams; high business value; medium-to-high difficulty.
2. **AI automation consulting / company** — commercial; operations and technology leaders; high value; high difficulty.
3. **AI agent governance / human-in-the-loop agents** — commercial/informational; risk, security, AI governance teams; high value; medium difficulty.
4. **Cybersecurity automation** — commercial/problem-based; security leaders; high value; medium-high difficulty.
5. **Cyber-risk visibility / security operations automation** — commercial/problem-based; CISO/SOC; high value; medium difficulty.
6. **OSINT automation / legal-tech OSINT** — commercial/informational; investigations, legal, risk, intelligence; high value; medium difficulty.
7. **Burlington / Ontario cybersecurity consulting** — local-commercial; Ontario SMB/municipal/enterprise buyers; high value; low-to-medium difficulty.
8. **ClearGlass / AgentOps / BLUEDESK / CG-OS Artemis** — branded; existing prospects and referral traffic; very high business value; low difficulty.

### Geographic rule
Create local/service-area pages only where ClearGlass genuinely operates or serves customers. Burlington/Ontario can be prioritized. Toronto may be used as a service-market page if supported by operations. New York/United States should be described as a service market only if factual; never invent an office, address, team, reviews, or local-business listing.

---

# D. Technical SEO fixes

| Priority | Fix | Expected effect |
|---|---|---|
| Critical | Declare one canonical production web surface and prevent preview/test metadata conflicts | Entity/canonical consolidation |
| Critical | Expand/generate sitemap from canonical indexable routes | Discovery and index management |
| Critical | Establish claim registry and remove/qualify unsupported certification/performance claims | Trust and factual integrity |
| High | Add per-page unique title, description, canonical, OG URL/image and Twitter metadata | SERP/social clarity |
| High | Add Organization + WebSite schema on home, BreadcrumbList on child pages, Service/Product/Article only where valid | Entity understanding |
| High | Build real HTML product/service/category pages instead of relying on anchors or Markdown files | Query ownership and internal linking |
| High | Instrument GA4/GTM events for CTA, form, consultation, download, newsletter, outbound checkout | Conversion measurement |
| High | Add Google Search Console and Bing Webmaster Tools verification + sitemap submission | Search monitoring |
| High | Performance-test and bound animation work; pause animation when page hidden | CWV/page-experience protection |
| Medium | Audit every image for meaningful alt text, dimensions, compression, lazy loading below fold | Accessibility + performance |
| Medium | Crawl internal links for 4xx, 5xx, redirect chains, orphan pages and mixed canonical forms | Crawl efficiency |
| Medium | Add author/reviewer, methodology, limitations, references and last-reviewed fields to editorial templates | E-E-A-T/trust and AI citation quality |
| Medium | Add noindex to utility/previews that should not rank | Index hygiene |
| Low | Consider a human-curated `llms.txt` only as an optional source map; never treat it as a Google ranking mechanism | Limited crawler usability |

### Core Web Vitals targets
- LCP: **≤ 2.5 s** at the 75th percentile.
- INP: **≤ 200 ms** at the 75th percentile.
- CLS: **≤ 0.1** at the 75th percentile.

No numeric ClearGlass CWV score is claimed until Search Console/CrUX or reproducible Lighthouse data is attached.

---

# E. 90-day content calendar

## Ten pillar pages

1. Governed AI Agents: Architecture, Controls, and Auditability
2. Enterprise AI Automation: From Workflow Discovery to Controlled Deployment
3. Cybersecurity Automation: A Practical Operating Model for Security Teams
4. AI Agent Governance: Human Approval, Tool Permissions, Evals, and Audit Trails
5. OSINT Automation: Evidence, Provenance, and Investigation Workflows
6. Cyber-Risk Visibility: Turning Security Signals Into Executive Decisions
7. Secure AgentOps: Operating Autonomous and Semi-Autonomous AI Systems
8. Legal-Tech OSINT: Defensible Research and Evidence Workflows
9. DevSecOps for AI Systems: Policy, CI/CD, Runtime Controls, and Rollback
10. AI Automation in Ontario: Governance, Security, and Implementation Guide

## Thirty supporting articles

### Governed AI / AgentOps
1. What is a governed AI agent?
2. Human-in-the-loop vs human-on-the-loop AI agents
3. How to design least-privilege tool access for AI agents
4. What an AI agent audit trail should contain
5. How to evaluate an AI agent before production
6. Prompt governance vs model governance
7. How to prevent AI tool abuse in enterprise workflows
8. Agent rollback and kill-switch design
9. How to measure agent reliability without vanity metrics
10. Building an evidence-bound AI copilot

### Cybersecurity / DevSecOps
11. How to automate security operations without automating bad decisions
12. Security automation maturity model for SMB and enterprise teams
13. What to automate first in a SOC
14. Cyber-risk visibility for executives: signals that matter
15. How to connect security controls to business evidence
16. CI/CD security controls for AI-enabled applications
17. Zero-trust controls for AI agents and automation
18. Threat-modeling autonomous workflows
19. Secure secrets management for agentic applications
20. Designing reversible security automation

### OSINT / legal-tech / investigation
21. OSINT automation without losing provenance
22. How to preserve evidence lineage in automated research
23. OSINT collection vs analysis vs inference
24. Building an OSINT confidence-scoring framework
25. Legal-tech research automation: where human review is mandatory
26. How to document assumptions in automated investigations
27. Entity resolution for OSINT: common failure modes
28. Building defensible investigation timelines
29. Ethical boundaries for public-source intelligence automation
30. How to create an evidence packet from multi-source OSINT

## Ten comparison pages

1. AI agents vs RPA
2. Agentic AI vs workflow automation
3. Human-in-the-loop vs fully autonomous agents
4. AI agent platform vs custom agent development
5. SOAR vs AI-driven security automation
6. SIEM vs cyber-risk visibility platform
7. Manual OSINT vs OSINT automation
8. Knowledge graph vs vector search for investigations
9. Rules-based automation vs LLM-based automation
10. Build vs buy for enterprise AI agents

**Rule:** Comparison pages must be factual, neutral, useful, and non-defamatory. Do not fabricate competitor limitations.

## Ten case-study / technical-briefing ideas

Until customer permission and results exist, publish these as **technical briefings**, not customer case studies:

1. Governed incident-triage agent reference architecture
2. Human-approved OSINT enrichment pipeline
3. Agent tool-permission threat model
4. Audit-ready AI workflow event schema
5. Reversible security automation control plane
6. Evidence-bound executive cyber-risk brief
7. Multi-source entity-resolution architecture
8. Secure agent deployment with canary and rollback
9. AI workflow approval-gate design patterns
10. Ontario SMB cyber/AI governance assessment methodology

## Ten linkable assets / tools

1. AI Agent Governance Readiness Assessment
2. Security Automation Maturity Scorecard
3. AI Agent Tool-Permission Matrix Template
4. Agent Audit-Trail Checklist
5. OSINT Evidence Provenance Checklist
6. Cyber-Risk Executive Brief Template
7. AI Workflow Threat-Model Canvas
8. Build-vs-Buy AI Agent Calculator
9. AI Automation ROI Assumption Calculator
10. DevSecOps AI Release-Gate Checklist

## Social distribution

### 12 LinkedIn posts
1. “The most dangerous AI agent is not the smartest one. It is the one with poorly governed tools.”
2. Five fields every agent audit log should capture.
3. Why “fully autonomous” is often the wrong enterprise goal.
4. A one-page diagram of human approval gates.
5. Security automation: reversible first, autonomous second.
6. Three signs a workflow is ready for AI automation.
7. OSINT without provenance is research debt.
8. Why agent evals belong in CI/CD.
9. From security alert to executive evidence.
10. Build vs buy: the hidden cost is governance integration.
11. Ontario AI adoption: governance as deployment infrastructure.
12. Technical briefing launch with one diagram and one practical takeaway.

### 12 X posts/threads
Repurpose the same 12 themes into concise technical threads with one diagram, checklist, or code/control example each. Avoid duplicate text across channels; link to the canonical article with campaign UTMs.

### Eight video concepts
1. Governed AI agent in 5 minutes
2. Human approval gates explained visually
3. Agent tool-abuse threat model walkthrough
4. Security automation maturity model
5. OSINT evidence lineage demo
6. Agent audit logs: what good looks like
7. Build vs buy AI agents
8. ClearGlass architecture briefing: evidence → decision → approved action

### Four newsletters
1. The Governed Agent Brief
2. Security Automation Without Loss of Control
3. Evidence-First OSINT
4. AI Operations: Evals, Approvals, Rollback

### Four digital-PR angles
1. Original survey/report: “Ontario AI Governance Readiness” — only after collecting a real sample and publishing methodology.
2. Expert commentary: security implications of autonomous tool-using agents.
3. Open reference asset: Agent Audit Trail Schema / control checklist.
4. Data-backed technical study: common AI-agent permission failures in public open-source projects, using a reproducible method and responsible disclosure.

## 13-week cadence

| Week | Primary deliverable | Supporting work |
|---|---|---|
| 1 | Technical/canonical fixes | Analytics + claim registry |
| 2 | Company, AI automation, cybersecurity destination pages | Internal linking |
| 3 | Governed AI Agents pillar | 2 supporting articles |
| 4 | Agent governance assessment tool | LinkedIn/X/video distribution |
| 5 | Cybersecurity Automation pillar | 2 supporting articles |
| 6 | Security Automation scorecard | Technical briefing #1 |
| 7 | OSINT Automation pillar | 2 supporting articles |
| 8 | Evidence provenance checklist | Technical briefing #2 |
| 9 | AgentOps product page | Comparison page #1 |
| 10 | BLUEDESK product page | Comparison page #2 |
| 11 | Ontario AI Automation pillar | Local authority outreach |
| 12 | DevSecOps for AI Systems pillar | Technical briefing #3 |
| 13 | Refresh winners, merge cannibalizing pages | Q4 measurement review |

---

# F. Page-by-page optimization briefs

## 1. Company overview
- **URL:** `/`
- **Title:** ClearGlass Inc. | Governed AI Automation & Cybersecurity
- **Meta:** ClearGlass Inc. designs governed AI automation, cybersecurity, agent systems, OSINT workflows and enterprise technology architectures with human approval and auditability.
- **Intent:** branded + commercial discovery
- **H1:** Governed AI automation and cybersecurity for high-stakes operations
- **Outline:** What ClearGlass does → Capabilities → Products/platforms → Operating methodology → Evidence/technical briefings → Markets served → Contact
- **FAQ:** What does ClearGlass Inc. do? What is governed AI automation? Where does ClearGlass operate? How does ClearGlass control AI-agent actions?
- **Schema:** Organization + WebSite; do not add LocalBusiness unless eligibility and physical-location facts are verified.
- **Internal links:** AI automation, cybersecurity, OSINT, AgentOps, BLUEDESK, methodology, case studies/briefings, contact.
- **Primary CTA:** Request an architecture briefing
- **Secondary CTA:** Run the governance readiness assessment
- **Evidence:** legal entity name, locations/service areas, approved product names, leadership, security/privacy claims.
- **Author/reviewer:** ClearGlass editorial owner + technical/security reviewer.
- **Freshness:** quarterly or on material product/company change.

## 2. Products & platforms
- **URL:** `/products/`
- **Title:** ClearGlass Products & Platforms | Governed AI and Cyber Operations
- **Meta:** Explore verified ClearGlass products and platforms for governed AI agents, cyber operations, intelligence workflows and enterprise automation.
- **Intent:** branded/commercial
- **H1:** ClearGlass products and platforms
- **Outline:** product cards → who each is for → capability matrix → governance model → request briefing.
- **FAQ:** Which ClearGlass platform fits my use case? Are products software, services, or blueprints? How are deployments governed?
- **Schema:** ItemList; Product only on individual product pages where product facts are valid.
- **CTA:** Compare platforms / Request briefing
- **Evidence:** registry ownership, status, availability, pricing wording.
- **Freshness:** monthly catalog check.

## 3. AI automation service
- **URL:** `/services/ai-automation/`
- **Title:** AI Automation Consulting & Agent Systems | ClearGlass Inc.
- **Meta:** Design governed AI automations and agent workflows with explicit permissions, evaluations, human approvals, audit trails and controlled deployment.
- **Intent:** commercial
- **H1:** Governed AI automation for enterprise workflows
- **Outline:** problems solved → discovery → architecture → governance → implementation → evals → deployment → FAQ.
- **Schema:** Service + BreadcrumbList
- **CTA:** Book an AI automation assessment
- **Evidence:** delivery methodology, examples that are clearly labeled demonstrations/reference designs unless customer-backed.
- **Freshness:** quarterly.

## 4. Cybersecurity service
- **URL:** `/services/cybersecurity/`
- **Title:** Cybersecurity Automation & Risk Visibility | ClearGlass Inc.
- **Meta:** Improve cyber-risk visibility and security operations with evidence-driven assessments, automation, control design and governed response workflows.
- **Intent:** commercial
- **H1:** Cybersecurity automation with evidence and control
- **Outline:** risk visibility → security automation → architecture review → control evidence → response governance → engagement model.
- **Schema:** Service + BreadcrumbList
- **CTA:** Request a cyber-risk assessment
- **Evidence:** frameworks used, exact scope, limitations; no unsupported certification claims.
- **Freshness:** quarterly + framework changes.

## 5. OSINT automation service
- **URL:** `/services/osint-automation/`
- **Title:** OSINT Automation & Evidence Workflows | ClearGlass Inc.
- **Meta:** Build OSINT workflows that preserve provenance, confidence, source boundaries, human review and defensible evidence trails.
- **Intent:** commercial/informational
- **H1:** OSINT automation built around evidence provenance
- **Outline:** collection vs analysis → provenance → entity resolution → confidence → review → legal/ethical boundaries → engagement.
- **Schema:** Service + BreadcrumbList
- **CTA:** Request an OSINT workflow review
- **Evidence:** methodology, source/legal boundaries, limitations.
- **Freshness:** quarterly.

## 6. AgentOps
- **URL:** `/products/agentops/`
- **Title:** ClearGlass AgentOps | Governed Enterprise AI Workflows
- **Meta:** Explore ClearGlass AgentOps for governed agent workflows, permissions, human approvals, evaluations, auditability and controlled enterprise automation.
- **Intent:** branded/commercial
- **H1:** Governed AgentOps for enterprise workflows
- **Outline:** product definition → architecture → controls → workflow examples → integrations → limitations → request demo.
- **Schema:** Product only if product status/offer facts are approved; otherwise SoftwareApplication/Service only if criteria are met and visible copy supports it.
- **CTA:** Request an AgentOps briefing
- **Evidence:** exact capabilities and deployment status.
- **Freshness:** monthly product review.

## 7. BLUEDESK
- **URL:** `/products/bluedesk/`
- **Title:** ClearGlass BLUEDESK | Defensive Security Operations
- **Meta:** Explore BLUEDESK defensive security workflows, operational visibility and governed automation from ClearGlass Inc.
- **Intent:** branded/commercial
- **H1:** BLUEDESK defensive security operations
- **Outline:** use case → operating model → controls → evidence → integrations → limitations → request briefing.
- **Schema:** Product/SoftwareApplication only after product facts are approved.
- **CTA:** Request a BLUEDESK briefing
- **Evidence:** actual capabilities, availability, integrations, status.
- **Freshness:** monthly product review.

## 8. Methodology
- **URL:** `/methodology/`
- **Title:** ClearGlass Methodology | Governed Automation and Evidence
- **Meta:** See how ClearGlass scopes, threat-models, evaluates, approves, deploys and audits AI automation and cybersecurity systems.
- **Intent:** trust/commercial validation
- **H1:** How ClearGlass builds governed systems
- **Outline:** discover → model risk → define controls → prototype → evaluate → approve → deploy → observe → rollback/improve.
- **Schema:** WebPage + BreadcrumbList
- **CTA:** Download the assessment checklist / Request a review
- **Evidence:** actual delivery process and reviewer ownership.
- **Freshness:** semiannual.

## 9. Technical briefings / case studies
- **URL:** `/briefings/` initially; migrate to `/case-studies/` only when verified customer evidence exists.
- **Title:** ClearGlass Technical Briefings | AI, Cybersecurity and OSINT
- **Meta:** Read evidence-led ClearGlass technical briefings on governed AI agents, security automation, OSINT provenance and enterprise architecture.
- **Intent:** informational + trust
- **H1:** Technical briefings and reference architectures
- **Schema:** CollectionPage; Article on individual briefings.
- **CTA:** Subscribe for technical briefings / Request an architecture review
- **Evidence:** citations, methodology, author/reviewer, limitations, update log.
- **Freshness:** review every 6–12 months.

## 10. Contact / qualification
- **URL:** `/contact/`
- **Title:** Contact ClearGlass Inc. | AI Automation & Cybersecurity
- **Meta:** Contact ClearGlass Inc. to discuss governed AI automation, cybersecurity, OSINT workflows, AgentOps or technical architecture.
- **Intent:** transactional
- **H1:** Discuss your system, risk, or automation goal
- **Outline:** qualification form → what happens next → engagement types → privacy note → response expectations only if operationally guaranteed.
- **Schema:** ContactPage + Organization reference
- **CTA:** Submit qualified inquiry
- **Evidence:** monitored contact method and privacy handling.
- **Freshness:** quarterly contact-route test.

---

# G. Internal-linking plan

| Source | Destination | Anchor | Reason | Funnel | Priority |
|---|---|---|---|---|---|
| Home | AI automation | governed AI automation | Establish service authority | Discovery | Critical |
| Home | Cybersecurity | cybersecurity automation | Commercial path | Discovery | Critical |
| Home | OSINT | OSINT automation | Commercial path | Discovery | High |
| Home | Products | ClearGlass products and platforms | Brand ownership | Discovery | High |
| AI automation | AgentOps | ClearGlass AgentOps | Service → product | Consideration | High |
| AI automation | Methodology | governance and evaluation methodology | Trust | Consideration | High |
| Cybersecurity | BLUEDESK | BLUEDESK defensive operations | Service → product | Consideration | High |
| Cybersecurity | Methodology | evidence-driven security methodology | Trust | Consideration | High |
| OSINT | OSINT provenance article | evidence provenance in OSINT | Depth | Consideration | Medium |
| AgentOps | Governed AI Agents pillar | governed AI agents | Explain category | Consideration | High |
| BLUEDESK | Cybersecurity Automation pillar | cybersecurity automation | Explain category | Consideration | High |
| Every pillar | Relevant service | implementation help | Convert informational traffic | Conversion | High |
| Every comparison | Relevant service/product | evaluate your architecture | Convert comparison traffic | Conversion | High |
| Technical briefings | Methodology | how ClearGlass evaluates systems | Evidence chain | Consideration | Medium |
| Methodology | Contact | request an architecture review | Final action | Conversion | High |
| Footer | Security | security | Trust/navigation | All | Medium |
| Footer | Privacy | privacy | Trust/navigation | All | Medium |
| Footer | Contact | contact ClearGlass | Conversion | All | Medium |

---

# H. Authority and digital PR plan

## Priority authority channels

- Burlington Chamber of Commerce: pursue a complete, factual member/business profile if membership is appropriate; use the legal business name, canonical domain, consistent description, and real contact information.
- Ontario Chamber of Commerce ecosystem and relevant local business directories: prioritize reputable, maintained directories; avoid bulk directory submission services.
- Canadian technology/cybersecurity media and newsletters: pitch original research, reference architectures, practitioner commentary, and data-backed findings rather than company announcements with no evidence.
- AI/cybersecurity conferences and meetups in Ontario/Canada/US: submit technical talks on governed agents, auditability, reversible automation, or OSINT provenance. Verify each event's current CFP before outreach.
- Podcasts/newsletters serving CISOs, AI governance leaders, DevSecOps teams, legal-tech, and investigations: pitch a concrete lesson, dataset, checklist, or architecture — not generic founder promotion.

## Legitimate link acquisition

1. Publish the agent-governance assessment with transparent scoring methodology.
2. Publish a reusable agent audit-trail schema.
3. Publish open templates/checklists with stable canonical URLs.
4. Publish original research with reproducible method, sample limitations, and downloadable data where lawful.
5. Contribute expert commentary when the topic matches demonstrated ClearGlass expertise.
6. Create partner integration pages only for real integrations/relationships.
7. Ask organizations that already mention ClearGlass to link to the most relevant canonical resource when editorially appropriate.

**Never:** buy ranking links, trade links at scale, use PBNs, mass-submit to low-quality directories, fabricate quotes/reviews, or place hidden keyword links.

---

# I. Conversion optimization plan

## CTA architecture

| Page type | Primary CTA | Secondary CTA | Lead magnet |
|---|---|---|---|
| Home | Request architecture briefing | Run readiness assessment | Governance readiness score |
| AI automation | Book AI automation assessment | View AgentOps | Workflow discovery worksheet |
| Cybersecurity | Request cyber-risk assessment | View BLUEDESK | Security automation scorecard |
| OSINT | Request OSINT workflow review | Read evidence guide | Provenance checklist |
| Product | Request product briefing/demo | View methodology | Product-specific architecture brief |
| Pillar article | Get implementation assessment | Subscribe | Checklist/template relevant to topic |
| Comparison | Evaluate your architecture | Download comparison matrix | Build-vs-buy worksheet |

## Contact-form improvements

Use 5–7 fields maximum initially:
- Work email
- Name
- Organization
- Role
- Primary objective (select)
- Time horizon (select)
- Free-text context (optional)

Add consent/privacy text, spam protection, success event, error event, and source/UTM capture. Do not ask for sensitive security details in a public form.

## A/B tests

1. “Request a briefing” vs “Request an architecture review.”
2. Hero proof order: capabilities first vs methodology first.
3. Assessment CTA in hero vs after first proof block.
4. Short qualification form vs staged two-step form.
5. Product CTA: “Request demo” vs “Discuss deployment.”

Run one material variable per experiment and predefine success metrics.

## Analytics events

- `view_service`
- `view_product`
- `cta_click`
- `assessment_start`
- `assessment_complete`
- `lead_form_start`
- `lead_form_submit`
- `lead_form_error`
- `newsletter_subscribe`
- `briefing_download`
- `outbound_product_click`
- `qualified_lead` (CRM/server-side where possible)
- `meeting_booked`

### UTM convention

`utm_source=<platform>`
`utm_medium=<organic_social|email|partner|pr|community>`
`utm_campaign=2026q3_<cluster>_<asset>`
`utm_content=<creative-or-anchor>`
`utm_term=<optional-paid-or-controlled-test-term>`

Example: `utm_campaign=2026q3_governed_agents_readiness_assessment`

---

# J. Prioritized implementation backlog

| Priority | Task | Impact | Effort | Technical owner | Content owner | Dependencies | Metric | Week |
|---|---|---|---|---|---|---|---|---|
| Critical | Establish canonical production surface/domain rules | Very high | M | Web/Platform | SEO | Deployment decision | canonical conflicts = 0 | 1 |
| Critical | Replace 2-URL sitemap with canonical route inventory/generator | Very high | M | Web | SEO | Route inventory | valid indexed URLs discovered | 1 |
| Critical | Create claim registry and review homepage/product claims | Very high | M | Security/Product | Editorial | Evidence owners | unverified claims published = 0 | 1 |
| High | Implement company-level homepage metadata/entity schema | High | S | Web | SEO | Approved company description | branded CTR / impressions | 1 |
| High | Launch AI automation destination page | High | M | Web | SEO/Technical | Approved service scope | non-brand impressions/leads | 2 |
| High | Launch cybersecurity destination page | High | M | Web | SEO/Security | Approved service scope | non-brand impressions/leads | 2 |
| High | Launch OSINT destination page | High | M | Web | Technical | Legal/ethical scope | impressions/qualified leads | 3 |
| High | Launch products index + AgentOps + BLUEDESK canonical pages | High | L | Web/Product | Product marketing | Product verification | branded product ownership | 3–4 |
| High | Implement analytics conversion events + UTM capture | High | M | Analytics/Web | Growth | GA4/GTM/CRM access | organic lead CVR | 1–2 |
| High | Connect GSC + Bing Webmaster Tools and submit sitemap | High | S | SEO/Web | — | Account access | coverage/crawl visibility | 1 |
| High | Benchmark and optimize CWV/animation CPU | High | M | Frontend | — | Lighthouse/CrUX | LCP/INP/CLS pass | 2 |
| Medium | Create methodology + technical briefing templates | Medium-high | M | Web | Technical editorial | Reviewer workflow | assisted conversions | 3 |
| Medium | Publish first governed-agent pillar + two support articles | Medium-high | L | Web | Technical editorial | Brief/template | non-brand clicks | 3–4 |
| Medium | Launch readiness assessment | High | L | Web | Growth/Technical | Scoring method + analytics | assessment leads | 4 |
| Medium | Build internal-link QA into CI | Medium | M | Platform | SEO | Route manifest | broken links/orphans = 0 | 4 |
| Medium | Establish quarterly content refresh queue | Medium | S | — | Editorial | Search data | decaying pages refreshed | 5 |
| Low | Optional `llms.txt` source map | Low/uncertain | S | Web | SEO | Stable canonical pages | crawler pickup if measurable | after core fixes |

---

# K. Measurement dashboard specification

## Search visibility
- Branded impressions, clicks, CTR, average position
- Non-branded impressions, clicks, CTR, average position
- Keyword-cluster visibility: governed AI, AI automation, cybersecurity automation, OSINT, local Ontario, products
- Landing pages gaining/losing clicks
- Search feature appearance where available

## Acquisition and engagement
- Organic sessions
- Engaged organic sessions
- Organic landing-page engagement rate
- Returning organic visitors
- Newsletter subscriptions from organic
- Assessment starts/completions

## Revenue/conversion
- Organic qualified leads
- Demo/briefing requests
- Organic lead conversion rate
- Meetings booked
- Assisted conversions
- Pipeline/revenue influenced by organic when CRM attribution supports it

## Authority
- Referring domains
- Editorially earned backlinks
- Links to tools/research vs homepage-only links
- Unlinked brand mentions worth legitimate outreach

## Technical/indexation
- Indexed canonical pages
- Excluded pages by reason
- Crawl errors
- 4xx/5xx responses
- Redirect chains
- Sitemap submitted vs indexed
- Canonical mismatch count
- Core Web Vitals pass rate

## AI-search visibility
Track only what is reproducibly measurable:
- Manual benchmark prompts by topic and market, monthly, with date/model/source recorded
- Citations/mentions to ClearGlass pages when surfaced
- Referral traffic from AI assistants where referrer data exists
- Landing pages repeatedly cited by answer engines

Do **not** invent an “AI visibility score” unless its methodology is documented and reproducible.

---

# L. Five actions ClearGlass should complete this week

1. **Resolve canonical ownership:** make `www.clearglassinc.com` the single search authority and eliminate conflicting preview metadata/indexation.
2. **Fix sitemap architecture:** build a canonical route inventory and submit the resulting sitemap to Google and Bing.
3. **Create the claim registry:** verify product names, locations, compliance wording, quantitative stats, availability, and all proof statements before expansion.
4. **Launch two commercial destination pages:** AI Automation and Cybersecurity, each with one clear CTA, methodology proof, FAQs, valid schema, and analytics events.
5. **Connect measurement:** Search Console, Bing Webmaster Tools, GA4/GTM and CRM attribution; capture a baseline before the 90-day publishing cadence begins.

## Publishing gate

A page is not “SEO complete” until it passes all of the following:

- Canonical 200-status URL
- Unique intent and no material cannibalization
- Factual claim review completed
- Direct answer near top
- One H1 and logical H2/H3 structure
- Useful internal links in and out
- Valid visible-content-matching schema only
- Accessible media and stable layout
- Primary + secondary CTA instrumented
- Author/reviewer + update date for editorial content
- Methodology/references/limitations when claims require them
- Sitemap inclusion if indexable
- Noindex if not intended for search
- Mobile and CWV validation
