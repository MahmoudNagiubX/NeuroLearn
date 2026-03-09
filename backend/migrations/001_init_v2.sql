-- =====================================================
-- NeuroLearn Phase 1 Database Schema (cleaned v2)
-- =====================================================
-- Changes in v2:
--  - tightened ownership with NOT NULL user_id columns
--  - added updated_at trigger support
--  - added stronger analytics/search indexes
--  - expanded tasks for ordering + recurrence + archival
--  - improved study session tracking (planned vs actual)
--  - improved pomodoro logging for analytics
--  - expanded attachment metadata for future ingestion
--  - changed app_events.event_type from ENUM to TEXT for flexibility

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- SHARED FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ENUMS
-- =====================================================

CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'done', 'archived');
CREATE TYPE session_status AS ENUM ('scheduled', 'in_progress', 'completed', 'missed', 'canceled');
CREATE TYPE pomodoro_status AS ENUM ('completed', 'aborted');
CREATE TYPE pomodoro_session_type AS ENUM ('focus', 'short_break', 'long_break');

-- =====================================================
-- USERS
-- =====================================================

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  full_name TEXT,
  is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_users_email_not_blank CHECK (length(trim(email)) > 0)
);

CREATE TRIGGER trg_users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- USER SETTINGS
-- =====================================================

CREATE TABLE user_settings (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  timezone TEXT NOT NULL DEFAULT 'Africa/Cairo',
  daily_study_goal_minutes INT NOT NULL DEFAULT 120 CHECK (daily_study_goal_minutes > 0),
  pomodoro_focus_minutes INT NOT NULL DEFAULT 25 CHECK (pomodoro_focus_minutes > 0),
  pomodoro_break_minutes INT NOT NULL DEFAULT 5 CHECK (pomodoro_break_minutes >= 0),
  pomodoro_long_break_minutes INT NOT NULL DEFAULT 15 CHECK (pomodoro_long_break_minutes >= 0),
  pomodoro_sessions_before_long_break INT NOT NULL DEFAULT 4 CHECK (pomodoro_sessions_before_long_break > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_user_settings_set_updated_at
BEFORE UPDATE ON user_settings
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- SUBJECTS / COURSES
-- =====================================================

CREATE TABLE subjects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  color TEXT,
  term TEXT,
  exam_date DATE,
  credit_hours NUMERIC(4,1) CHECK (credit_hours IS NULL OR credit_hours >= 0),
  is_archived BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_subjects_user_name UNIQUE (user_id, name),
  CONSTRAINT chk_subjects_name_not_blank CHECK (length(trim(name)) > 0)
);

CREATE INDEX idx_subjects_user_id ON subjects(user_id);
CREATE INDEX idx_subjects_user_archived ON subjects(user_id, is_archived);

CREATE TRIGGER trg_subjects_set_updated_at
BEFORE UPDATE ON subjects
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- TASK LISTS
-- =====================================================

CREATE TABLE task_lists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_task_lists_user_name UNIQUE (user_id, name),
  CONSTRAINT chk_task_lists_name_not_blank CHECK (length(trim(name)) > 0)
);

CREATE INDEX idx_task_lists_user_id ON task_lists(user_id);

CREATE TRIGGER trg_task_lists_set_updated_at
BEFORE UPDATE ON task_lists
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- TASKS
-- =====================================================

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  list_id UUID REFERENCES task_lists(id) ON DELETE SET NULL,

  title TEXT NOT NULL,
  description TEXT,

  status task_status NOT NULL DEFAULT 'todo',
  priority SMALLINT NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
  position INT NOT NULL DEFAULT 0,

  due_at TIMESTAMPTZ,
  reminder_at TIMESTAMPTZ,

  estimated_minutes INT CHECK (estimated_minutes IS NULL OR estimated_minutes > 0),
  completed_at TIMESTAMPTZ,
  archived_at TIMESTAMPTZ,

  is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
  recurrence_rule TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_tasks_title_not_blank CHECK (length(trim(title)) > 0),
  CONSTRAINT chk_tasks_recurrence_consistency CHECK (
    (is_recurring = FALSE AND recurrence_rule IS NULL)
    OR (is_recurring = TRUE AND recurrence_rule IS NOT NULL)
  ),
  CONSTRAINT chk_tasks_completed_status CHECK (
    (status <> 'done') OR completed_at IS NOT NULL
  ),
  CONSTRAINT chk_tasks_archived_status CHECK (
    archived_at IS NULL OR status = 'archived'
  )
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_subject_id ON tasks(subject_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_due_at ON tasks(user_id, due_at);
CREATE INDEX idx_tasks_user_list_position ON tasks(user_id, list_id, position);

CREATE TRIGGER trg_tasks_set_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- TAGS
-- =====================================================

CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_tags_user_name UNIQUE (user_id, name),
  CONSTRAINT chk_tags_name_not_blank CHECK (length(trim(name)) > 0)
);

CREATE INDEX idx_tags_user_id ON tags(user_id);

CREATE TRIGGER trg_tags_set_updated_at
BEFORE UPDATE ON tags
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE task_tags (
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);

-- =====================================================
-- STUDY SESSIONS (PLANNER)
-- =====================================================

CREATE TABLE study_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,

  title TEXT,

  scheduled_start TIMESTAMPTZ NOT NULL,
  scheduled_end TIMESTAMPTZ NOT NULL,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,

  planned_duration_minutes INT CHECK (planned_duration_minutes IS NULL OR planned_duration_minutes > 0),
  actual_duration_minutes INT CHECK (actual_duration_minutes IS NULL OR actual_duration_minutes >= 0),

  focus_rating SMALLINT CHECK (focus_rating IS NULL OR focus_rating BETWEEN 1 AND 5),
  difficulty_rating SMALLINT CHECK (difficulty_rating IS NULL OR difficulty_rating BETWEEN 1 AND 5),
  progress_rating SMALLINT CHECK (progress_rating IS NULL OR progress_rating BETWEEN 1 AND 5),

  notes TEXT,
  summary TEXT,

  status session_status NOT NULL DEFAULT 'scheduled',

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_study_sessions_schedule_window CHECK (scheduled_end > scheduled_start),
  CONSTRAINT chk_study_sessions_start_before_complete CHECK (
    completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at
  )
);

CREATE INDEX idx_study_sessions_user_id ON study_sessions(user_id);
CREATE INDEX idx_study_sessions_subject_id ON study_sessions(subject_id);
CREATE INDEX idx_study_sessions_user_scheduled_start ON study_sessions(user_id, scheduled_start);
CREATE INDEX idx_study_sessions_user_status ON study_sessions(user_id, status);

CREATE TRIGGER trg_study_sessions_set_updated_at
BEFORE UPDATE ON study_sessions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- POMODORO SESSIONS
-- =====================================================

CREATE TABLE pomodoro_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  study_session_id UUID REFERENCES study_sessions(id) ON DELETE SET NULL,

  session_type pomodoro_session_type NOT NULL DEFAULT 'focus',
  planned_minutes INT NOT NULL CHECK (planned_minutes > 0),
  actual_minutes INT CHECK (actual_minutes IS NULL OR actual_minutes >= 0),
  focus_minutes INT CHECK (focus_minutes IS NULL OR focus_minutes >= 0),
  break_minutes INT CHECK (break_minutes IS NULL OR break_minutes >= 0),

  interruptions INT NOT NULL DEFAULT 0 CHECK (interruptions >= 0),
  distraction_count INT NOT NULL DEFAULT 0 CHECK (distraction_count >= 0),
  abandon_reason TEXT,

  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ NOT NULL,

  status pomodoro_status NOT NULL DEFAULT 'completed',

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_pomodoro_sessions_time_window CHECK (ended_at > started_at)
);

CREATE INDEX idx_pomodoro_sessions_user_id ON pomodoro_sessions(user_id);
CREATE INDEX idx_pomodoro_sessions_user_started_at ON pomodoro_sessions(user_id, started_at);
CREATE INDEX idx_pomodoro_sessions_user_type ON pomodoro_sessions(user_id, session_type);

CREATE TRIGGER trg_pomodoro_sessions_set_updated_at
BEFORE UPDATE ON pomodoro_sessions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- NOTE FOLDERS
-- =====================================================

CREATE TABLE note_folders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  parent_id UUID REFERENCES note_folders(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_note_folders_name_not_blank CHECK (length(trim(name)) > 0)
);

CREATE INDEX idx_note_folders_user_id ON note_folders(user_id);
CREATE INDEX idx_note_folders_parent_id ON note_folders(parent_id);

CREATE TRIGGER trg_note_folders_set_updated_at
BEFORE UPDATE ON note_folders
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- NOTES
-- =====================================================

CREATE TABLE notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  folder_id UUID REFERENCES note_folders(id) ON DELETE SET NULL,

  title TEXT NOT NULL,
  content_md TEXT NOT NULL,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_notes_title_not_blank CHECK (length(trim(title)) > 0)
);

CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_subject_id ON notes(subject_id);
CREATE INDEX idx_notes_user_subject_id ON notes(user_id, subject_id);
CREATE INDEX idx_notes_title ON notes(title);

CREATE TRIGGER trg_notes_set_updated_at
BEFORE UPDATE ON notes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================
-- NOTE TAGS
-- =====================================================

CREATE TABLE note_tags (
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (note_id, tag_id)
);

CREATE INDEX idx_note_tags_tag_id ON note_tags(tag_id);

-- =====================================================
-- NOTE ATTACHMENTS
-- =====================================================

CREATE TABLE note_attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  original_filename TEXT NOT NULL,
  file_extension TEXT,
  mime_type TEXT,
  file_size_bytes BIGINT CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0),
  checksum TEXT,

  storage_provider TEXT NOT NULL DEFAULT 's3',
  storage_key TEXT NOT NULL,
  upload_status TEXT NOT NULL DEFAULT 'uploaded',

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_note_attachments_filename_not_blank CHECK (length(trim(original_filename)) > 0),
  CONSTRAINT chk_note_attachments_storage_key_not_blank CHECK (length(trim(storage_key)) > 0)
);

CREATE INDEX idx_note_attachments_note_id ON note_attachments(note_id);
CREATE INDEX idx_note_attachments_user_id ON note_attachments(user_id);
CREATE INDEX idx_note_attachments_upload_status ON note_attachments(upload_status);

-- =====================================================
-- APP EVENT LOGGING
-- =====================================================

CREATE TABLE app_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  event_type TEXT NOT NULL,
  entity_type TEXT,
  entity_id UUID,

  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_app_events_event_type_not_blank CHECK (length(trim(event_type)) > 0)
);

CREATE INDEX idx_app_events_user_id ON app_events(user_id);
CREATE INDEX idx_app_events_event_type ON app_events(event_type);
CREATE INDEX idx_app_events_occurred_at ON app_events(occurred_at);
CREATE INDEX idx_app_events_user_event_time ON app_events(user_id, event_type, occurred_at);
CREATE INDEX idx_app_events_metadata_gin ON app_events USING GIN (metadata);