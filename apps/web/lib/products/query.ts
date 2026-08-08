import type { CatalogFilters, ProductRecord, ProductSort } from "./domain";
import { productRegistry } from "./registry";

const normalized = (value: string) => value.trim().toLocaleLowerCase();
const includes = (values: readonly string[], query: string) => values.some((value) => normalized(value).includes(query));

export function rankProducts(products: readonly ProductRecord[], rawQuery: string) {
  const query = normalized(rawQuery);
  if (!query) return products.map((product) => ({ product, score: 0, reasons: [] as string[] }));
  return products.map((product) => {
    const name = normalized(product.name); let score = 0; const reasons: string[] = [];
    const add = (matched: boolean, points: number, reason: string) => { if (matched) { score += points; reasons.push(reason); } };
    add(name === query, 100, "exact name"); add(name.startsWith(query) && name !== query, 80, "name prefix");
    add(includes(product.aliases, query), 70, "alias"); add(normalized(product.family ?? "").includes(query), 65, "family");
    add(normalized(product.category).includes(query), 55, "category"); add(includes(product.capabilities, query), 50, "capability");
    add(includes(product.tags, query), 45, "tag"); add(includes(product.useCases, query), 40, "use case");
    add(includes([...product.outcomes, ...product.integrations, ...product.platforms, ...product.audience], query), 35, "portfolio metadata");
    add(normalized(product.description).includes(query), 20, "description"); add(normalized(product.sku ?? "").includes(query), 20, "SKU");
    return { product, score, reasons };
  }).filter((result) => result.score > 0).sort((a, b) => b.score - a.score || a.product.name.localeCompare(b.product.name));
}

export function searchProducts(query: string, products: readonly ProductRecord[] = productRegistry) { return rankProducts(products, query).map(({ product }) => product); }
export function filterProducts(products: readonly ProductRecord[], filters: CatalogFilters) { return products.filter((p) => (!filters.categories?.length || filters.categories.includes(p.category)) && (!filters.families?.length || (p.family && filters.families.includes(p.family))) && (!filters.statuses?.length || filters.statuses.includes(p.status))); }
export function sortProducts(products: readonly ProductRecord[], sort: ProductSort) { return [...products].sort((a, b) => sort === "name" ? a.name.localeCompare(b.name) : sort === "newest" ? (b.merchandising.launchDate ?? "").localeCompare(a.merchandising.launchDate ?? "") || a.name.localeCompare(b.name) : Number(b.recommended) - Number(a.recommended) || b.merchandising.priority - a.merchandising.priority || a.name.localeCompare(b.name)); }
export const getProductBySlug = (slug: string) => productRegistry.find((p) => p.slug === slug);
export const getProductsByCategory = (category: string) => productRegistry.filter((p) => p.category === category);
export const getFeaturedProducts = () => productRegistry.filter((p) => p.featured);
export const getFlagshipProducts = () => productRegistry.filter((p) => p.flagship);
export const getRelatedProducts = (product: ProductRecord) => product.relationships.related.map((id) => productRegistry.find((p) => p.id === id)).filter((p): p is ProductRecord => Boolean(p));
export const getComplementaryProducts = (product: ProductRecord) => product.relationships.complements.map((id) => productRegistry.find((p) => p.id === id)).filter((p): p is ProductRecord => Boolean(p));
export function getProductFacets(products: readonly ProductRecord[] = productRegistry) { const tally = (read: (p: ProductRecord) => string[]) => [...products.reduce((map, product) => { read(product).forEach((value) => map.set(value, (map.get(value) ?? 0) + 1)); return map; }, new Map<string, number>())].map(([value, count]) => ({ value, count })).sort((a, b) => a.value.localeCompare(b.value)); return { categories: tally((p) => [p.category]), families: tally((p) => p.family ? [p.family] : []), statuses: tally((p) => [p.status]), platforms: tally((p) => p.platforms), audiences: tally((p) => p.audience), pricing: tally((p) => p.pricing ? [p.pricing.type] : []) }; }
export const getCatalogStatistics = () => ({ products: productRegistry.length, families: new Set(productRegistry.map((p) => p.family).filter(Boolean)).size, available: productRegistry.filter((p) => p.status === "available").length });
