-- Bring app_events schema in sync with ORM model.
-- 003_add_app_events.sql used CREATE TABLE IF NOT EXISTS, which does not
-- add columns when app_events already exists from 001_init_v2.sql.

ALTER TABLE app_events
    ADD COLUMN IF NOT EXISTS subject_id UUID;

ALTER TABLE app_events
    ADD COLUMN IF NOT EXISTS task_id UUID;

ALTER TABLE app_events
    ADD COLUMN IF NOT EXISTS study_session_id UUID;

ALTER TABLE app_events
    ADD COLUMN IF NOT EXISTS pomodoro_session_id UUID;

ALTER TABLE app_events
    ADD COLUMN IF NOT EXISTS note_id UUID;

ALTER TABLE app_events
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

UPDATE app_events
SET metadata = '{}'::jsonb
WHERE metadata IS NULL;

ALTER TABLE app_events
    ALTER COLUMN metadata SET DEFAULT '{}'::jsonb,
    ALTER COLUMN metadata SET NOT NULL;
