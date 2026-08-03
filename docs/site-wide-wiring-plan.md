# ClearGlassInc Artemis Site-Wide Wiring Plan

## Experience architecture

The website now operates as a three-layer journey without removing any existing content:

1. **Orient — corporate overview (`index.html`)**: establish the mission, capabilities, platform suite, architecture, thought leadership, and briefing path.
2. **Evaluate — CG-OS flagship (`CG-os.html`)**: move technical buyers through architecture, ontology, agents, safe self-improvement, Python implementation, governance, and an end-to-end scenario.
3. **Operate — mission control (`apps/web`)**: demonstrate the live evidence graph, signal triage, agent registry, immutable audit, and two-person approval behavior.

The primary narrative is **signal → context → governed recommendation → human decision → measured improvement**. Navigation labels and CTA bridges should reinforce this sequence rather than expose repository structure.

## Page-by-page flow map

| Surface | Journey role | Entry paths | Additive connections | Intended next step |
| --- | --- | --- | --- | --- |
| Corporate overview | Awareness and qualification | Search, direct visit, campaign | Contextual links after About and Platforms; a four-step journey map; flagship links retain deep-link context | Enter CG-OS architecture or request briefing |
| CG-OS flagship | Technical evaluation and trust | Overview hero, architecture CTA, direct visit | Home affordance, breadcrumb, sequential next-section bridges, closing conversion panel | Complete scenario, then request briefing |
| Mission control | Product proof and operational confidence | Product demonstration environment | Reusable experience breadcrumb with Overview, CG-OS, current location, and briefing CTA | Return to product context or engage sales |
| Technical blueprint | Deep implementation validation | Architecture section and CG-OS code | Keep as a long-form reference; link readers back to product narrative in future document-rendering work | Security review or briefing |
| Campaign article | Thought leadership and acquisition | Blog section, organic search | Keep its existing direct CTA; future article templates should include topic-adjacent CG-OS deep links | Architecture evaluation |

## Additive navigation system

- **Global layer:** logo/home, flagship entry, architecture, editorial content, and contact remain stable.
- **Context layer:** breadcrumbs explain the relationship between corporate, product, and operational surfaces.
- **Progression layer:** “Next in the system” modules make long technical pages scannable and sequential.
- **Conversion layer:** each high-intent journey ends in one clear, mission-relevant briefing action.
- **Accessibility layer:** semantic `nav`, ordered journey steps, `aria-current`, visible focus states, descriptive labels, and reduced-motion support.

## CTA and internal-link placement rules

1. Place a contextual bridge after a user has received enough evidence to understand the next topic; do not interrupt explanatory content.
2. Deep-link to the most relevant section (for example, `CG-os.html#architecture`) instead of always targeting a page top.
3. Use action labels that predict the destination: “Explore the governed system architecture” is preferable to “Learn more.”
4. Preserve one primary and one secondary CTA in hero regions; downstream bridges should be visually quieter.
5. Carry users back to the corporate briefing section from the end of technical and operational journeys.

## Modular implementation strategy

- Treat `ExperienceNav` as the application-level navigation primitive. Extend its data array when new application routes are introduced.
- Keep static-site bridge patterns (`journey-step`, `context-link`, `nextBridge`, `conversionBridge`) visually related through shared cyan/gold tokens and semantic link markup.
- When the static pages migrate into the application shell, convert these patterns into `JourneyMap`, `ContextLink`, `NextStep`, and `ConversionBridge` components without changing their information architecture.
- Add analytics events for journey selection, cross-surface transitions, scenario completion, and briefing intent. Do not include classified mission identifiers or free-text rationale in marketing analytics.
- Measure progression rate, qualified briefing conversion, return-to-overview rate, section completion, keyboard navigation success, and Core Web Vitals by surface.
- Preserve server-rendered links and descriptive anchor text for crawlability. Avoid navigation that depends solely on client-side state.

## Growth guardrails

- Every new page must declare its journey role, primary predecessor, primary successor, and fallback route to either the overview or briefing.
- New product modules should deep-link into a relevant CG-OS concept before asking for conversion.
- Operational actions remain inside authenticated applications; public pages explain capabilities but never simulate authority or bypass approval.
- Performance polish should prefer CSS transitions, progressive enhancement, and reduced-motion alternatives over navigation-blocking animation.
