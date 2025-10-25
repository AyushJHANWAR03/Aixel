CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type text NOT NULL,
  timestamp timestamptz NOT NULL DEFAULT now(),
  session_id text,
  user_id text,
  page_url text,
  utm_source text,
  utm_medium text,
  utm_campaign text,
  platform text,
  device text,
  revenue numeric,
  metadata jsonb
);

CREATE INDEX idx_events_timestamp ON events (timestamp);
CREATE INDEX idx_events_session ON events (session_id);
