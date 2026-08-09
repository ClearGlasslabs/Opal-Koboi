import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { productRegistry } from "../../lib/products/registry";
import { getCatalogStatistics, getFlagshipProducts } from "../../lib/products/query";
import { ProductCatalog } from "./ProductCatalog";

export const metadata: Metadata = { title: "Product Intelligence | ClearGlassInc Artemis", description: "Explore the ClearGlassInc Artemis governed intelligence portfolio by capability, mission outcome, and deployment model.", alternates: { canonical: "/products" }, openGraph: { title: "ClearGlassInc Artemis Product Intelligence", description: "A governed portfolio navigator for mission intelligence systems.", url: "/products", type: "website" } };

export default function ProductsPage() {
  const stats = getCatalogStatistics(); const flagship = getFlagshipProducts()[0];
  return <main className="productsShell">
    <nav className="productsNav"><Link href="/" className="productsBrand"><b>A</b><span>CLEARGLASSINC<small>ARTEMIS / PRODUCT INTELLIGENCE</small></span></Link><Link href="/#platform-promise">Platform</Link><a href="https://www.clearglassinc.com/#contact">Secure briefing ↗</a></nav>
    <header className="productsHero"><div><p>PRODUCT INTELLIGENCE OPERATING SYSTEM / 01</p><h1>Find the system.<br/><em>Understand the mission fit.</em></h1><span>One authoritative portfolio surface for discovery, technical evidence, comparison, and governed conversion.</span></div><aside><small>PORTFOLIO TELEMETRY</small><dl><div><dt>Systems</dt><dd>{stats.products.toString().padStart(2, "0")}</dd></div><div><dt>Families</dt><dd>{stats.families.toString().padStart(2, "0")}</dd></div><div><dt>Flagship</dt><dd>{flagship?.name ?? "—"}</dd></div></dl></aside></header>
    <section className="familyRail"><p>PORTFOLIO FAMILY</p>{[...new Set(productRegistry.map((p) => p.family).filter(Boolean))].map((family) => <article key={family}><small>FAMILY / {family}</small><h2>{family}</h2><p>{productRegistry.filter((p) => p.family === family).length} system · {productRegistry.find((p) => p.family === family)?.outcomes[0]}</p></article>)}</section>
    <Suspense fallback={<p className="catalogLoading">Loading product intelligence…</p>}><ProductCatalog products={[...productRegistry]} /></Suspense>
    <footer className="productsFooter"><span>© 2026 ClearGlassInc Artemis</span><a href="/legal">Privacy · Terms · AUP</a><span>Commercial data shown only when authoritative.</span></footer>
  </main>;
}
