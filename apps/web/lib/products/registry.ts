import { productSchema, type ProductRecord } from "./domain";
import { publicProductSource } from "./source";

export type RegistryIssue = { index: number; code: string; message: string };

export function buildProductRegistry(source: readonly unknown[]): { products: ProductRecord[]; issues: RegistryIssue[] } {
  const products: ProductRecord[] = [];
  const issues: RegistryIssue[] = [];
  source.forEach((entry, index) => {
    const result = productSchema.safeParse(entry);
    if (result.success) products.push(result.data);
    else issues.push({ index, code: "INVALID_PRODUCT", message: result.error.issues.map((issue) => `${issue.path.join(".")}: ${issue.message}`).join("; ") });
  });
  const uniqueFields: Array<[keyof ProductRecord | "stripePriceId", (product: ProductRecord) => string | undefined]> = [
    ["id", (p) => p.id], ["slug", (p) => p.slug], ["sku", (p) => p.sku], ["stripePriceId", (p) => p.commerce?.stripePriceId],
  ];
  uniqueFields.forEach(([field, read]) => {
    const seen = new Map<string, number>();
    products.forEach((product, index) => {
      const value = read(product);
      if (!value) return;
      const previous = seen.get(value);
      if (previous !== undefined) issues.push({ index, code: `DUPLICATE_${String(field).toUpperCase()}`, message: `${String(field)} '${value}' duplicates product at normalized index ${previous}` });
      else seen.set(value, index);
    });
  });
  const ids = new Set(products.map((product) => product.id));
  products.forEach((product, index) => Object.values(product.relationships).flat().forEach((id) => {
    if (!ids.has(id)) issues.push({ index, code: "ORPHAN_RELATIONSHIP", message: `${product.id} references unknown product '${id}'` });
  }));
  return { products: products.sort((a, b) => b.merchandising.priority - a.merchandising.priority || a.name.localeCompare(b.name)), issues };
}

const built = buildProductRegistry(publicProductSource);
if (built.issues.length && process.env.NODE_ENV !== "production") console.error("Product registry validation failed", built.issues);
export const productRegistry = Object.freeze(built.products);
export const productRegistryIssues = Object.freeze(built.issues);
