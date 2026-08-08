import type { Snapshot } from "./contracts";

export async function getPublicSnapshot(stream = "public"): Promise<Snapshot> {
  const enabled = process.env.LIVE_PUBLIC_ENABLED === "true" && Boolean(process.env.LIVE_STATUS_SOURCE_URL);
  if (!enabled) return { stream, enabled: false, signal: { status: "unavailable", message: "Verified live source not configured", freshness: { state: "unavailable" } } };
  // Provider adapters are deliberately fail-closed until their authorization and data scope are approved.
  return { stream, enabled: false, signal: { status: "unavailable", message: "Source pending owner approval", freshness: { state: "unavailable" } } };
}
