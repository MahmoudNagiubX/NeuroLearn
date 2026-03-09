# 🧠 NeuroLearn — Phase 1 Database Design Blueprint

## 🎯 Goal

Define the full Phase 1 database design before implementation.

This step should lock:
* core entities
* relationships
* table responsibilities
* required fields
* optional fields
* ownership rules
* event data structure
* attachment metadata structure

This step is critical because the database becomes the foundation for:
* backend models
* Alembic migrations
* repositories
* APIs
* analytics
* future AI data pipelines

---

## 📋 What Step 4 Will Cover

### 1. Core Phase 1 Tables 🗄️
We will define the final Phase 1 tables for:
* users
* user_settings
* subjects
* tasks
* study_sessions
* pomodoro_sessions
* notes
* tags
* note_tags
* note_attachments
* app_events

### 2. Table-by-Table Purpose 📝
For each table we will define:
* why it exists
* what it stores
* how it connects to other tables

### 3. Relationships 🔗
We will define all important relationships such as:
* one user → many subjects
* one subject → many tasks
* one subject → many study sessions
* one note → many attachments
* many notes ↔ many tags

### 4. Ownership Rules 🔐
We will define which tables must contain:
* user_id
* subject_id
* note_id
* task_id

This is required for security and clean data access.

### 5. Analytics-Supporting Fields 📊
We will make sure the schema supports later metrics such as:
* study duration
* task completion trends
* subject productivity
* focus behavior
* note activity
* event history

### 6. Future-Proofing 🚀
We will also ensure the Phase 1 schema does not block later phases such as:
* RAG ingestion
* adaptive learning
* burnout prediction
* recommendation systems
* graph intelligence

---

## ❓ Why Step 4 Comes Next

Step 1 defined the product scope.
Step 2 defined the architecture.
Step 3 defined backend engineering rules.
Now Step 4 defines the **actual data foundation**.

Without Step 4:
* backend models cannot be created correctly
* migrations cannot be created correctly
* repositories cannot be designed correctly
* APIs will become unstable later

---

## ➡️ What Comes After Step 4

After the database blueprint, the next step should be:

### Step 5 — Backend API Design Blueprint 🔌
That step will define:
* endpoint groups
* request/response responsibilities
* module-by-module API contracts
* authentication flow
* ownership and permission behavior

---

## 📅 Current Correct Order

1. Phase 1 Product Blueprint
2. System Architecture
3. Backend Engineering Standards
4. Database Design Blueprint
5. API Design Blueprint
6. Backend implementation start
7. Frontend architecture and screen design
8. Frontend implementation
9. Analytics implementation
10. file handling and attachment flow
11. deployment setup

---

# 🧠 NeuroLearn Database Schema (Final Tables)

## 🎯 Goal

Define the **actual PostgreSQL schema** for Phase 1.

This schema supports:
* authentication
* subjects
* tasks
* study sessions
* pomodoro tracking
* notes
* attachments
* tags
* analytics queries
* behavior events

All tables use **UUID primary keys** and **timestamps**.

---

# 🗄️ Core Tables

## users
Purpose: store user accounts.

Fields:
* id (UUID PK)
* name
* email (unique)
* password_hash
* created_at
* updated_at

Relationships:
* users → subjects
* users → tasks
* users → notes
* users → study_sessions
* users → events

---

## user_settings
Purpose: store study preferences.

Fields:
* id (UUID PK)
* user_id (FK users)
* timezone
* daily_study_goal_minutes
* default_focus_minutes
* default_break_minutes
* created_at
* updated_at

Relationship:
* one user → one settings record

---

# 📚 Subjects

## subjects
Purpose: academic containers.

Fields:
* id (UUID PK)
* user_id (FK users)
* name
* description
* color
* exam_date
* is_archived
* created_at
* updated_at

Relationships:
* subjects → tasks
* subjects → study_sessions
* subjects → notes

---

# ✅ Tasks

## tasks
Purpose: planned study work.

Fields:
* id (UUID PK)
* user_id (FK users)
* subject_id (FK subjects)
* title
* description
* priority
* status
* due_date
* estimated_minutes
* created_at
* updated_at

Relationships:
* tasks → study_sessions

---

# ⏱️ Study Sessions

## study_sessions
Purpose: record real study activity.

Fields:
* id (UUID PK)
* user_id (FK users)
* subject_id (FK subjects)
* task_id (FK tasks nullable)
* scheduled_start
* started_at
* completed_at
* planned_duration_minutes
* actual_duration_minutes
* focus_rating
* difficulty_rating
* progress_rating
* summary
* status
* created_at
* updated_at

Relationships:
* study_sessions → pomodoro_sessions

---

# 🍅 Pomodoro Tracking

## pomodoro_sessions
Purpose: track focus cycles.

Fields:
* id (UUID PK)
* user_id (FK users)
* study_session_id (FK study_sessions)
* focus_duration_minutes
* break_duration_minutes
* long_break_minutes
* cycles_planned
* cycles_completed
* interruptions
* started_at
* completed_at
* created_at
* updated_at

---

# 📝 Notes

## notes
Purpose: learning notes.

Fields:
* id (UUID PK)
* user_id (FK users)
* subject_id (FK subjects)
* title
* content
* folder
* created_at
* updated_at

Relationships:
* notes → attachments
* notes ↔ tags

---

# 🏷️ Tags

## tags
Purpose: label notes.

Fields:
* id (UUID PK)
* user_id (FK users)
* name
* created_at
* updated_at

---

## note_tags
Purpose: many-to-many relation.

Fields:
* id (UUID PK)
* note_id (FK notes)
* tag_id (FK tags)

---

# 📎 Attachments

## note_attachments
Purpose: metadata for uploaded files.

Fields:
* id (UUID PK)
* user_id (FK users)
* note_id (FK notes)
* original_filename
* file_type
* file_size
* storage_key
* created_at

Files are stored in **object storage**.

---

# 📡 Event Tracking

## app_events
Purpose: store behavior logs.

Fields:
* id (UUID PK)
* user_id (FK users)
* event_type
* entity_type
* entity_id
* metadata (JSONB)
* occurred_at

Used later for:
* analytics
* productivity tracking
* ML features

---

# 🔗 Relationships Summary

users  
├── user_settings  
├── subjects  
│   ├── tasks  
│   ├── study_sessions  
│   │   └── pomodoro_sessions  
│   └── notes  
│       ├── note_attachments  
│       └── note_tags  
│           └── tags  
└── app_events

---

# ⚡ Required Indexes

Create indexes for:
* users.email
* subjects.user_id
* tasks.subject_id
* tasks.user_id
* study_sessions.user_id
* study_sessions.subject_id
* notes.user_id
* notes.subject_id
* note_attachments.note_id
* app_events.user_id
* app_events.event_type

---

# 🔒 Required Constraints

Important constraints:
* users.email unique
* foreign keys enforced
* tasks must belong to subjects
* notes must belong to subjects
* attachments must belong to notes

---

# 🏁 Step 6 Summary

Phase 1 database includes:

Core entities:
* users
* user_settings
* subjects
* tasks
* study_sessions
* pomodoro_sessions
* notes
* tags
* note_tags
* note_attachments
* app_events

This schema supports:
* productivity tracking
* learning activity
* analytics
* event history
* future AI features
