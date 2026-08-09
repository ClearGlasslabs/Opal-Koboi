"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { formatPrice, getProductCta, type ProductRecord, type ProductSort } from "../../lib/products/domain";
import { filterProducts, getProductFacets, rankProducts, sortProducts } from "../../lib/products/query";
import { trackProductEvent } from "../../lib/products/analytics";

type Density = "intelligence" | "standard" | "compact";
const MAX_COMPARE = 4;

export function ProductCatalog({ products }: { products: ProductRecord[] }) {
  const params = useSearchParams(); const router = useRouter(); const pathname = usePathname();
  const [query, setQuery] = useState(params.get("q") ?? "");
  const [category, setCategory] = useState(params.get("category") ?? "");
  const [family, setFamily] = useState(params.get("family") ?? "");
  const [sort, setSort] = useState<ProductSort>((params.get("sort") as ProductSort) || "recommended");
  const [density, setDensity] = useState<Density>((params.get("view") as Density) || "intelligence");
  const [matrix, setMatrix] = useState(params.get("matrix") === "1");
  const [inspect, setInspect] = useState<ProductRecord>();
  const [compare, setCompare] = useState<string[]>([]);
  const inspectorRef = useRef<HTMLDialogElement>(null); const lastTrigger = useRef<HTMLElement | null>(null);
  const facets = useMemo(() => getProductFacets(products), [products]);
  const results = useMemo(() => { const searched = query ? rankProducts(products, query).map((r) => r.product) : products; return sortProducts(filterProducts(searched, { categories: category ? [category] : [], families: family ? [family] : [] }), sort); }, [products, query, category, family, sort]);
  const capabilities = useMemo(() => [...new Set(results.flatMap((p) => p.capabilities))].sort(), [results]);

  useEffect(() => { const restoreComparison = window.setTimeout(() => { try { const saved = JSON.parse(localStorage.getItem("cg-product-compare") ?? "[]"); if (Array.isArray(saved)) setCompare(saved.filter((id) => products.some((p) => p.id === id)).slice(0, MAX_COMPARE)); } catch { localStorage.removeItem("cg-product-compare"); } }, 0); trackProductEvent("catalog_view", { surface: "catalog" }); return () => window.clearTimeout(restoreComparison); }, [products]);
  useEffect(() => { const next = new URLSearchParams(); if (query) next.set("q", query); if (category) next.set("category", category); if (family) next.set("family", family); if (sort !== "recommended") next.set("sort", sort); if (density !== "intelligence") next.set("view", density); if (matrix) next.set("matrix", "1"); const timer = window.setTimeout(() => router.replace(`${pathname}${next.size ? `?${next}` : ""}`, { scroll: false }), 250); return () => clearTimeout(timer); }, [query, category, family, sort, density, matrix, pathname, router]);
  useEffect(() => { if (!inspect) return; const dialog = inspectorRef.current; dialog?.showModal(); const close = () => setInspect(undefined); dialog?.addEventListener("close", close); return () => dialog?.removeEventListener("close", close); }, [inspect]);

  const toggleCompare = (product: ProductRecord) => setCompare((current) => { const removing = current.includes(product.id); const next = removing ? current.filter((id) => id !== product.id) : current.length < MAX_COMPARE ? [...current, product.id] : current; localStorage.setItem("cg-product-compare", JSON.stringify(next)); trackProductEvent(removing ? "comparison_remove" : "comparison_add", { productId: product.id, family: product.family, category: product.category, surface: "catalog" }); return next; });
  const openInspector = (product: ProductRecord, trigger: HTMLElement) => { lastTrigger.current = trigger; setInspect(product); trackProductEvent("quick_view_open", { productId: product.id, family: product.family, category: product.category, surface: "catalog" }); };
  const reset = () => { setQuery(""); setCategory(""); setFamily(""); setSort("recommended"); trackProductEvent("filter_clear", { surface: "catalog" }); };

  return <>
    <section className="productDeck" aria-label="Product catalog controls">
      <div className="productSearch"><label htmlFor="product-search">Search product intelligence</label><input id="product-search" type="search" value={query} placeholder="Product, capability, outcome…" onChange={(e) => { setQuery(e.target.value); trackProductEvent("product_search", { query: e.target.value, surface: "catalog" }); }} /></div>
      <label>Family<select value={family} onChange={(e) => setFamily(e.target.value)}><option value="">All families</option>{facets.families.map((f) => <option key={f.value} value={f.value}>{f.value} · {f.count}</option>)}</select></label>
      <label>Category<select value={category} onChange={(e) => setCategory(e.target.value)}><option value="">All categories</option>{facets.categories.map((f) => <option key={f.value} value={f.value}>{f.value} · {f.count}</option>)}</select></label>
      <label>Sort<select value={sort} onChange={(e) => { setSort(e.target.value as ProductSort); trackProductEvent("sort_change", { surface: "catalog" }); }}><option value="recommended">Recommended</option><option value="name">Name</option><option value="newest">Newest</option></select></label>
      <label>Density<select value={density} onChange={(e) => setDensity(e.target.value as Density)}><option value="intelligence">Intelligence</option><option value="standard">Standard</option><option value="compact">Compact</option></select></label>
      <button type="button" aria-pressed={matrix} onClick={() => setMatrix((v) => !v)}>Matrix</button><button type="button" onClick={reset}>Reset</button>
      <p className="productResults" role="status" aria-live="polite"><b>{results.length}</b> of {products.length} systems</p>
    </section>
    {(query || category || family) && <div className="activeFilters" aria-label="Active filters">Active: {query && <button onClick={() => setQuery("")}>Search: {query} ×</button>} {family && <button onClick={() => setFamily("")}>{family} ×</button>} {category && <button onClick={() => setCategory("")}>{category} ×</button>}</div>}
    {matrix ? <div className="matrixScroller" tabIndex={0} aria-label="Product capability matrix"><table><caption>Capabilities derived from canonical product metadata</caption><thead><tr><th>Capability</th>{results.map((p) => <th key={p.id}>{p.name}</th>)}</tr></thead><tbody>{capabilities.map((capability) => <tr key={capability}><th>{capability}</th>{results.map((p) => <td key={p.id} aria-label={`${p.name}: ${p.capabilities.includes(capability) ? "supported" : "not specified"}`}>{p.capabilities.includes(capability) ? "✓" : "—"}</td>)}</tr>)}</tbody></table></div> :
      <div className={`productGrid density-${density}`}>{results.map((product, position) => <article className="productCard" key={product.id}>
        <header><span>{product.family ?? product.category}</span>{product.merchandising.ribbon && <b>{product.merchandising.ribbon}</b>}<em>{product.status.replace("-", " ")}</em></header>
        <div className="productVisual" aria-hidden="true"><span>{product.name.slice(0, 2).toUpperCase()}</span></div>
        <div className="productIdentity"><p>{product.category}</p><h2>{product.name}</h2><strong>{product.outcomes[0] ?? product.summary}</strong><p>{product.summary ?? product.description}</p></div>
        <div className="productEvidence"><small>CORE CAPABILITIES</small><ul>{product.capabilities.slice(0, density === "compact" ? 2 : density === "standard" ? 3 : 5).map((c) => <li key={c}>{c}</li>)}</ul></div>
        <div className="productCommercial"><small>COMMERCIAL MODEL</small><b>{formatPrice(product)}</b></div>
        <div className="productActions"><Link className="productPrimary" href={getProductCta(product).href} aria-disabled={getProductCta(product).disabled} onClick={() => trackProductEvent(getProductCta(product).kind === "checkout" ? "checkout_start" : getProductCta(product).kind === "contact" ? "contact_sales" : "product_open", { productId: product.id, family: product.family, category: product.category, position, surface: "catalog" })}>{getProductCta(product).label}</Link><button type="button" onClick={(e) => openInspector(product, e.currentTarget)}>Inspect</button><label><input type="checkbox" checked={compare.includes(product.id)} disabled={!compare.includes(product.id) && compare.length >= MAX_COMPARE} onChange={() => toggleCompare(product)} /> Compare</label></div>
      </article>)}</div>}
    {!results.length && <section className="productEmpty"><h2>No matching systems</h2><p>Remove a filter or broaden the search. No product data was discarded.</p><button onClick={reset}>Reset catalog</button></section>}
    {compare.length > 0 && <aside className="compareTray" aria-label="Comparison workspace"><div><small>COMPARISON WORKSPACE</small><b>{compare.length} / {MAX_COMPARE} selected</b></div>{compare.map((id) => { const product = products.find((p) => p.id === id)!; return <span key={id}>{product.name}<button aria-label={`Remove ${product.name}`} onClick={() => toggleCompare(product)}>×</button></span> })}<button onClick={() => { setCompare([]); localStorage.removeItem("cg-product-compare"); }}>Clear</button></aside>}
    {inspect && <dialog ref={inspectorRef} className="productInspector" onClose={() => lastTrigger.current?.focus()} aria-labelledby="inspector-title"><button className="inspectorClose" onClick={() => inspectorRef.current?.close()} aria-label="Close inspector">×</button><small>{inspect.family} / {inspect.status}</small><h2 id="inspector-title">{inspect.name}</h2><p>{inspect.summary ?? inspect.description}</p><h3>Capabilities</h3><ul>{inspect.capabilities.map((c) => <li key={c}>{c}</li>)}</ul><p><b>Platforms:</b> {inspect.platforms.join(", ") || "Not specified"}</p><p><b>Commercial model:</b> {formatPrice(inspect)}</p><div className="inspectorActions"><Link href={inspect.links.details}>Full product intelligence</Link><Link href={getProductCta(inspect).href}>{getProductCta(inspect).label}</Link></div></dialog>}
  </>;
}
