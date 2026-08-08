import { z } from "zod";

export const productStatusSchema = z.enum([
  "available", "beta", "preview", "coming-soon", "enterprise", "discontinued",
]);

export const productSchema = z.object({
  id: z.string().min(1),
  slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  sku: z.string().min(1).optional(),
  name: z.string().min(1),
  aliases: z.array(z.string()).default([]),
  description: z.string().min(1),
  summary: z.string().optional(),
  family: z.string().optional(),
  category: z.string().min(1),
  tags: z.array(z.string()).default([]),
  status: productStatusSchema,
  tier: z.enum(["individual", "professional", "business", "enterprise"]).optional(),
  featured: z.boolean().default(false),
  flagship: z.boolean().default(false),
  recommended: z.boolean().default(false),
  pricing: z.discriminatedUnion("type", [
    z.object({ type: z.literal("quote") }),
    z.object({ type: z.literal("free") }),
    z.object({ type: z.enum(["one-time", "subscription", "usage"]), amount: z.number().finite().nonnegative(), currency: z.string().length(3), interval: z.enum(["month", "year"]).optional() }),
  ]).optional(),
  capabilities: z.array(z.string()).default([]),
  outcomes: z.array(z.string()).default([]),
  useCases: z.array(z.string()).default([]),
  integrations: z.array(z.string()).default([]),
  platforms: z.array(z.string()).default([]),
  audience: z.array(z.string()).default([]),
  deployment: z.array(z.string()).default([]),
  commerce: z.object({ stripeProductId: z.string().optional(), stripePriceId: z.string().optional(), checkoutUrl: z.string().url().optional() }).optional(),
  links: z.object({ details: z.string().startsWith("/products/"), demo: z.string().url().optional(), docs: z.string().url().optional(), contact: z.string().url().optional() }),
  relationships: z.object({ related: z.array(z.string()).default([]), complements: z.array(z.string()).default([]), upgradesTo: z.array(z.string()).default([]) }).default({ related: [], complements: [], upgradesTo: [] }),
  seo: z.object({ title: z.string().optional(), description: z.string().optional(), keywords: z.array(z.string()).default([]) }).default({ keywords: [] }),
  merchandising: z.object({ priority: z.number().int().default(0), launchDate: z.string().date().optional(), ribbon: z.string().optional() }).default({ priority: 0 }),
});

export type ProductRecord = z.infer<typeof productSchema>;
export type ProductStatus = z.infer<typeof productStatusSchema>;
export type ProductSort = "recommended" | "name" | "newest";
export type CatalogFilters = { categories?: string[]; families?: string[]; statuses?: ProductStatus[] };

export type ProductCta = { label: string; href: string; kind: "details" | "contact" | "checkout"; disabled?: boolean };

export function getProductCta(product: ProductRecord): ProductCta {
  if (product.status === "discontinued") return { label: "Unavailable", href: product.links.details, kind: "details", disabled: true };
  if (product.commerce?.checkoutUrl && product.status === "available") return { label: product.pricing?.type === "subscription" ? "Subscribe" : "Buy now", href: product.commerce.checkoutUrl, kind: "checkout" };
  if (product.status === "beta") return { label: "Request beta access", href: product.links.contact ?? product.links.details, kind: product.links.contact ? "contact" : "details" };
  if (product.status === "coming-soon" || product.status === "preview") return { label: "Learn more", href: product.links.details, kind: "details" };
  return { label: "Request consultation", href: product.links.contact ?? product.links.details, kind: product.links.contact ? "contact" : "details" };
}

export function formatPrice(product: ProductRecord): string {
  const price = product.pricing;
  if (!price || price.type === "quote") return "Contact for scope";
  if (price.type === "free") return "Free";
  const value = new Intl.NumberFormat("en", { style: "currency", currency: price.currency }).format(price.amount);
  return `${value}${price.interval ? ` / ${price.interval}` : ""}`;
}
