import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { formatPrice, getProductCta } from "../../../lib/products/domain";
import { productRegistry } from "../../../lib/products/registry";
import { getProductBySlug, getRelatedProducts } from "../../../lib/products/query";

export const dynamicParams = false;
export function generateStaticParams() { return productRegistry.map(({ slug }) => ({ slug })); }
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> { const product = getProductBySlug((await params).slug); if (!product) return {}; return { title: product.seo.title ?? product.name, description: product.seo.description ?? product.summary ?? product.description, keywords: product.seo.keywords, alternates: { canonical: product.links.details }, openGraph: { title: product.name, description: product.seo.description ?? product.description, type: "website", url: product.links.details } }; }

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const product = getProductBySlug((await params).slug); if (!product) notFound(); const cta = getProductCta(product); const related = getRelatedProducts(product);
  const jsonLd = { "@context": "https://schema.org", "@graph": [{ "@type": "SoftwareApplication", name: product.name, description: product.description, applicationCategory: product.category, operatingSystem: product.platforms.join(", "), url: `https://clearglasslabs.github.io/Opal-Koboi${product.links.details}` }, { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Products", item: "https://clearglasslabs.github.io/Opal-Koboi/products" }, { "@type": "ListItem", position: 2, name: product.name, item: `https://clearglasslabs.github.io/Opal-Koboi${product.links.details}` }] }] };
  return <main className="productDetail"><script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
    <nav><Link href="/products">← Product intelligence</Link><Link href="/">ClearGlassInc Artemis</Link></nav>
    <header><div><p>{product.family} / {product.category} / {product.status}</p><h1>{product.name}</h1><h2>{product.outcomes[0]}</h2><span>{product.summary ?? product.description}</span><div><a className="productPrimary" href={cta.href}>{cta.label}</a><Link href="#technical">Review technical intelligence ↓</Link></div></div><aside aria-label="Product identity"><span>{product.name.slice(0, 2).toUpperCase()}</span><small>GOVERNED SYSTEM / {product.merchandising.ribbon}</small></aside></header>
    <section className="detailMetrics"><div><small>COMMERCIAL MODEL</small><b>{formatPrice(product)}</b></div><div><small>DEPLOYMENT</small><b>{product.deployment.join(" · ") || "Not specified"}</b></div><div><small>PLATFORMS</small><b>{product.platforms.join(" · ") || "Not specified"}</b></div></section>
    <section id="technical" className="detailGrid"><article><small>01 / CORE CAPABILITIES</small><h2>Operational evidence</h2><ul>{product.capabilities.map((item) => <li key={item}>{item}</li>)}</ul></article><article><small>02 / USE CASES</small><h2>Mission applications</h2><ul>{product.useCases.map((item) => <li key={item}>{item}</li>)}</ul></article><article><small>03 / INTEGRATIONS</small><h2>Connected ecosystem</h2><ul>{product.integrations.map((item) => <li key={item}>{item}</li>)}</ul></article><article><small>04 / AUDIENCE</small><h2>Built for authority</h2><ul>{product.audience.map((item) => <li key={item}>{item}</li>)}</ul></article></section>
    {related.length > 0 && <section><h2>Related systems</h2>{related.map((item) => <Link key={item.id} href={item.links.details}>{item.name}</Link>)}</section>}
    <section className="detailConversion"><small>CONVERSION / HUMAN-GOVERNED</small><h2>Scope the mission, then authorize the system.</h2><p>No price or purchase identifier is inferred. Commercial configuration begins through an approved briefing.</p><a className="productPrimary" href={cta.href}>{cta.label}</a></section>
  </main>;
}
