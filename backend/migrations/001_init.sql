-- This schema includes:
--  - Users & authentication
--  - User settings
--  - Subjects (courses)
--  - Tasks & tags
--  - Study planner sessions
--  - Pomodoro sessions
--  - Notes & folders
--  - Attachments
--  - Event logging for analytics

-- =====================================================
-- NeuroLearn Phase 1 Database Schema
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- USERS
-- =====================================================

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  full_name TEXT,
  is_email_verified BOOLEAN DEFAULT FALSE,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- USER SETTINGS
-- =====================================================

CREATE TABLE user_settings (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  timezone TEXT DEFAULT 'Africa/Cairo',
  daily_study_goal_minutes INT DEFAULT 120,
  pomodoro_focus_minutes INT DEFAULT 25,
  pomodoro_break_minutes INT DEFAULT 5,
  pomodoro_long_break_minutes INT DEFAULT 15,
  pomodoro_sessions_before_long_break INT DEFAULT 4,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- SUBJECTS / COURSES
-- =====================================================

CREATE TABLE subjects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  color TEXT,
  term TEXT,
  exam_date TIMESTAMPTZ,
  credit_hours NUMERIC(4,1),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, name)
);

CREATE INDEX idx_subject_user ON subjects(user_id);

-- =====================================================
-- TASK LISTS
-- =====================================================

CREATE TABLE task_lists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, name)
);

-- =====================================================
-- TASKS
-- =====================================================

CREATE TYPE task_status AS ENUM ('todo','in_progress','done','archived');

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  list_id UUID REFERENCES task_lists(id) ON DELETE SET NULL,

  title TEXT NOT NULL,
  description TEXT,

  status task_status DEFAULT 'todo',

  priority SMALLINT DEFAULT 3 CHECK(priority BETWEEN 1 AND 5),
  due_at TIMESTAMPTZ,
  reminder_at TIMESTAMPTZ,

  estimated_minutes INT,
  completed_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_subject ON tasks(subject_id);
CREATE INDEX idx_tasks_due ON tasks(due_at);

-- =====================================================
-- TAGS
-- =====================================================

CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id,name)
);

CREATE TABLE task_tags (
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY(task_id,tag_id)
);

-- =====================================================
-- STUDY SESSIONS (PLANNER)
-- =====================================================

CREATE TYPE session_status AS ENUM ('scheduled','completed','missed','canceled');

CREATE TABLE study_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,

  title TEXT,

  start_at TIMESTAMPTZ NOT NULL,
  end_at TIMESTAMPTZ NOT NULL,

  status session_status DEFAULT 'scheduled',

  actual_minutes INT,

  notes TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CHECK (end_at > start_at)
);

CREATE INDEX idx_sessions_user ON study_sessions(user_id);
CREATE INDEX idx_sessions_start ON study_sessions(start_at);

-- =====================================================
-- POMODORO SESSIONS
-- =====================================================

CREATE TYPE pomodoro_status AS ENUM ('completed','aborted');

CREATE TABLE pomodoro_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  study_session_id UUID REFERENCES study_sessions(id) ON DELETE SET NULL,

  focus_minutes INT NOT NULL,
  break_minutes INT NOT NULL,

  interruptions INT DEFAULT 0,

  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ NOT NULL,

  status pomodoro_status DEFAULT 'completed',

  created_at TIMESTAMPTZ DEFAULT NOW(),

  CHECK(ended_at > started_at)
);

CREATE INDEX idx_pomodoro_user ON pomodoro_sessions(user_id);

-- =====================================================
-- NOTE FOLDERS
-- =====================================================

CREATE TABLE note_folders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  parent_id UUID REFERENCES note_folders(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- NOTES
-- =====================================================

CREATE TABLE notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
  folder_id UUID REFERENCES note_folders(id) ON DELETE SET NULL,

  title TEXT NOT NULL,
  content_md TEXT NOT NULL,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notes_user ON notes(user_id);

-- =====================================================
-- NOTE TAGS
-- =====================================================

CREATE TABLE note_tags (
  note_id UUID REFERENCES notes(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY(note_id,tag_id)
);

-- =====================================================
-- NOTE ATTACHMENTS
-- =====================================================

CREATE TABLE note_attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id UUID REFERENCES notes(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  file_name TEXT NOT NULL,
  mime_type TEXT,
  file_size_bytes BIGINT,

  storage_key TEXT NOT NULL,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- APP EVENT LOGGING
-- =====================================================

CREATE TYPE app_event_type AS ENUM (
  'task_created',
  'task_completed',
  'study_session_created',
  'study_session_completed',
  'pomodoro_started',
  'pomodoro_completed',
  'note_created',
  'note_updated',
  'login'
);

CREATE TABLE app_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  event_type app_event_type NOT NULL,

  entity_type TEXT,
  entity_id UUID,

  meta JSONB DEFAULT '{}'::jsonb,

  occurred_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_user ON app_events(user_id);
CREATE INDEX idx_events_time ON app_events(occurred_at);