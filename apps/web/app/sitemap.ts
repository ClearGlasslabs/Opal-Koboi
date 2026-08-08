import type { MetadataRoute } from "next";
import { productRegistry } from "../lib/products/registry";

export default function sitemap(): MetadataRoute.Sitemap { const origin = "https://clearglasslabs.github.io/Opal-Koboi"; return [{ url: origin, priority: 1 }, { url: `${origin}/products`, priority: 0.9 }, { url: `${origin}/legal`, priority: 0.4 }, ...productRegistry.map((product) => ({ url: `${origin}${product.links.details}`, priority: product.flagship ? 0.9 : 0.7 }))]; }
