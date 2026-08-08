import { z } from "zod";

export const connectionStates = ["CONNECTING", "LIVE", "DEGRADED", "STALE", "OFFLINE", "ERROR", "DISABLED"] as const;
export type ConnectionState = (typeof connectionStates)[number];
export const freshnessSchema = z.object({
  state: z.enum(["live", "recent", "cached", "stale", "estimated", "unavailable"]),
  measuredAt: z.iso.datetime().optional(), receivedAt: z.iso.datetime().optional(),
  expiresAt: z.iso.datetime().optional(), source: z.string().max(100).optional(),
});
export type DataFreshness = z.infer<typeof freshnessSchema>;
export const classificationSchema = z.enum(["PUBLIC", "AUTHENTICATED", "WORKSPACE", "ADMIN", "INTERNAL", "SECRET"]);
export const publicSignalSchema = z.object({ status: z.enum(["operational", "degraded", "incident", "unavailable"]), message: z.string().max(240), freshness: freshnessSchema });
export type PublicSignal = z.infer<typeof publicSignalSchema>;

const knownSources = new Set(["clearglass-health", "development-mock"]);
export const liveEventSchema = z.object({
  id: z.string().min(1).max(128), type: z.string().regex(/^[a-z]+(?:\.[a-z]+)+$/), version: z.literal(1),
  occurredAt: z.iso.datetime(), publishedAt: z.iso.datetime(), source: z.string().max(100),
  environment: z.enum(["development", "staging", "production"]),
  visibility: z.enum(["public", "authenticated", "internal"]), tenantId: z.string().max(100).optional(),
  correlationId: z.string().min(1).max(128), sequence: z.number().int().nonnegative(), payload: publicSignalSchema,
}).superRefine((event, context) => {
  if (!knownSources.has(event.source)) context.addIssue({ code: "custom", path: ["source"], message: "Unknown event source" });
  if (Date.parse(event.publishedAt) < Date.parse(event.occurredAt)) context.addIssue({ code: "custom", path: ["publishedAt"], message: "Publication precedes occurrence" });
  if (Date.parse(event.occurredAt) > Date.now() + 60_000) context.addIssue({ code: "custom", path: ["occurredAt"], message: "Future timestamp" });
});
export type LiveEvent = z.infer<typeof liveEventSchema>;
export type Snapshot = { stream: string; enabled: boolean; signal: PublicSignal; lastEventId?: string };
