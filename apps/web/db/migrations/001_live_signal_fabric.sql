CREATE TABLE IF NOT EXISTS live_events (
  id text PRIMARY KEY, event_type text NOT NULL, version integer NOT NULL,
  occurred_at timestamptz NOT NULL, published_at timestamptz NOT NULL,
  source text NOT NULL, environment text NOT NULL, visibility text NOT NULL,
  tenant_id text, correlation_id text NOT NULL, sequence bigint NOT NULL,
  payload jsonb NOT NULL, expires_at timestamptz NOT NULL,
  UNIQUE (source, tenant_id, sequence)
);
CREATE INDEX IF NOT EXISTS live_events_replay ON live_events (visibility, tenant_id, sequence);
CREATE TABLE IF NOT EXISTS live_stream_config (
  stream text PRIMARY KEY, enabled boolean NOT NULL DEFAULT false,
  classification text NOT NULL, owner_approved_at timestamptz, updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE live_events ENABLE ROW LEVEL SECURITY;
-- Deployment must install tenant policies using the authenticated session tenant claim.
