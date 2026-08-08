export type ProductAnalyticsEvent = "catalog_view" | "product_open" | "product_search" | "filter_apply" | "filter_clear" | "sort_change" | "comparison_add" | "comparison_remove" | "quick_view_open" | "checkout_start" | "contact_sales";
export type ProductAnalyticsContext = { productId?: string; family?: string; category?: string; query?: string; position?: number; surface: "catalog" | "inspector" | "detail" | "comparison" };

export function trackProductEvent(event: ProductAnalyticsEvent, context: ProductAnalyticsContext) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("clearglass:product", { detail: { event, ...context } }));
}
