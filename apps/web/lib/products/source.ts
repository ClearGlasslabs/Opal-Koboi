// Authoritative public catalog source. Commercial fields are intentionally absent
// until an approved price or checkout identifier exists.
export const publicProductSource = [
  {
    id: "cg-os-artemis",
    slug: "cg-os-artemis",
    name: "CG-OS Artemis",
    aliases: ["CG-OS", "Artemis"],
    description: "A governed product blueprint for coalition-aware intelligence operations across Palantir Gotham, Foundry, AIP, and Apollo.",
    summary: "Fuse live and historical signals into explainable, human-authorized decisions while continuously improving evaluated workflows.",
    family: "ARTEMIS",
    category: "Intelligence Operations",
    tags: ["governed AI", "ontology", "mission control"],
    status: "enterprise",
    tier: "enterprise",
    featured: true,
    flagship: true,
    recommended: true,
    pricing: { type: "quote" },
    capabilities: ["Live signal fusion", "Ontology-driven reasoning", "Human approval gates", "Audited self-improvement", "Controlled deployment"],
    outcomes: ["Defensible decisions with complete provenance"],
    useCases: ["Operational intelligence", "Entity investigations", "Mission planning"],
    integrations: ["Palantir Gotham", "Palantir Foundry", "Palantir AIP", "Palantir Apollo"],
    platforms: ["Cloud", "Edge", "Disconnected"],
    audience: ["Analysts", "Commanders", "Security teams"],
    deployment: ["Coalition-aware", "Multi-domain"],
    links: { details: "/products/cg-os-artemis", contact: "https://www.clearglassinc.com/#contact" },
    relationships: { related: [], complements: [], upgradesTo: [] },
    seo: { title: "CG-OS Artemis Product Intelligence", description: "Explore the governed ClearGlassInc Artemis intelligence operating system.", keywords: ["CG-OS", "ClearGlassInc Artemis", "governed intelligence"] },
    merchandising: { priority: 100, ribbon: "Flagship" },
  },
] satisfies unknown[];

export type PublicProductSource = typeof publicProductSource[number];
