import type { MetadataRoute } from "next";
import { productRegistry } from "../lib/products/registry";

const ORIGIN = "https://www.clearglassinc.com";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${ORIGIN}/`, priority: 1 },
    { url: `${ORIGIN}/products`, priority: 0.9 },
    ...productRegistry.map((product) => ({
      url: `${ORIGIN}${product.links.details}`,
      priority: product.flagship ? 0.9 : 0.7,
    })),
  ];
}
