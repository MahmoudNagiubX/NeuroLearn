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
