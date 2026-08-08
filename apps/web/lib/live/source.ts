import type { LiveEvent } from "./contracts";

export type SourceHealth = { available: boolean; checkedAt: string; detail?: string };
export type SnapshotInput = { stream: string; tenantId?: string };
export type SubscriptionInput = SnapshotInput & { afterId?: string; signal?: AbortSignal };
export interface LiveDataSource<T> {
  name: string;
  healthCheck(): Promise<SourceHealth>;
  fetchSnapshot(input: SnapshotInput): Promise<T>;
  subscribe(input: SubscriptionInput): AsyncIterable<LiveEvent>;
}

/** Development-only adapter: it never invents metrics and always reports unavailable. */
export class DisabledDevelopmentSource implements LiveDataSource<null> {
  name = "development-mock";
  async healthCheck() { return { available: false, checkedAt: new Date().toISOString(), detail: "No verified source configured" }; }
  async fetchSnapshot() { return null; }
  async *subscribe() { return; }
}
