# 🧠 NeuroLearn Phased MVP Strategy
### We will divide development into 5 phases:
| Phase | Focus | Systems |
| :--- | :--- | :--- |
| **Phase 1** | Productivity foundation | tasks + planner + notes + pomodoro + course manager + Authentication |
| **Phase 2** | AI study assistant | RAG study assistant + document intelligence |
| **Phase 3** | Adaptive learning | BKT, quizzes, mastery + Knowledge tracing |
| **Phase 4** | Research + coding | paper assistant + code analyzer |
| **Phase 5** | Advanced intelligence | GraphRAG + RL scheduling + burnout ML + prediction |

## 🚀 Phase 1 — Productivity & Data Foundation (MVP)
**Goal:** Build the platform students actually use daily and collect behavioral data. 
This phase creates the base system and database.

### 🛠️ Systems included
* **Authentication**
    * Login / signup
    * JWT authentication
* **User Settings & Profile**
    * username
    * study goal hours/day
    * preferred pomodoro duration
    * timezone
* **Course / Subject Manager**
    * create subject
    * edit subject
    * assign color
    * optional exam date
    * optional credit hours
* **To-Do List**
    * Tasks (linked to subjects)
    * priorities
    * deadlines
    * completion tracking
* **Study Planner**
    * calendar view
    * study session scheduling
    * link sessions to tasks
* **Pomodoro Timer**
    * focus sessions
    * break sessions
    * interruptions logging
* **Study Counter**
    * track study hours
    * subject distribution
    * weekly consistency
* **Notes System**
    * markdown notes
    * folders
    * tags
    * subject linking
    * basic search
* **Note Attachments (File Storage)**
    * PDFs
    * lecture slides
    * screenshots
* **Basic Analytics Dashboard**
    * study time graphs
    * tasks completed
    * focus sessions
    * analytics per subject

**🎯 Result of Phase 1**
* NeuroLearn becomes a structured productivity platform for students.
* This phase generates the core behavioral logs, subject connections, and file foundations needed for future ML models and the RAG system.

---

## 🤖 Phase 2 — AI Study Assistant (RAG System)
**Goal:** Turn the system into an AI learning assistant.

### 🛠️ Systems included
* **Document Upload System**
    * PDFs
    * lecture slides
    * notes
* **Document Processing Pipeline**
    * text extraction
    * chunking
    * embeddings generation
* **Vector Database**
    * FAISS or Pinecone
* **Semantic Search**
* **RAG Assistant**
    * Users can ask: *“Explain the Fourier Transform from my notes”*
    * The system retrieves relevant chunks and generates grounded answers.
* **AI Study Tools**
    * summaries
    * flashcards
    * quiz generation
    * beginner vs advanced explanation modes

**🎯 Result of Phase 2**
* NeuroLearn becomes an AI study companion.

---

## 📈 Phase 3 — Adaptive Learning Engine
**Goal:** Turn the assistant into a personalized learning system.

### 🛠️ Systems included
* **Quiz Engine**
    * MCQ questions
    * conceptual questions
    * coding challenges
* **Knowledge Tracing**
    * Bayesian Knowledge Tracing (BKT)
    * Track: correctness, response time, attempts, confidence
* **Difficulty Adaptation**
    * Item Response Theory (IRT)
    * Multi-Armed Bandits
* **Skill Mastery Model**
    * Example output: 
        * Linear Algebra → 72% mastery
        * Dynamic Programming → 43%
        * Graphs → 58%
* **Mastery Dashboard**
    * weak concept detection
    * learning path suggestions

**🎯 Result of Phase 3**
* NeuroLearn becomes an adaptive AI tutor.

---

## 🔬 Phase 4 — Research & Coding Intelligence
**Goal:** Make NeuroLearn powerful for technical students.

### 🛠️ Systems included
* **1. AI Research Paper Assistant**
    * **Features:** summarize papers, extract methodology, dataset detection, compare papers, related work suggestions
    * **Advanced:** citation graph modeling
* **2. AI Code Interview Analyzer**
    * **Pipeline:**
  
    ```
     Code submission
          ↓
      AST parsing
          ↓
    test case evaluation
          ↓
    complexity estimation
          ↓
    optimization suggestions
    ```
    * **Metrics tracked:** solution accuracy, time complexity, improvement history

**🎯 Result of Phase 4**
* NeuroLearn becomes: Study system + research assistant + coding trainer

---

## 🧬 Phase 5 — Advanced Intelligence Layer
**Goal:** Add research-level AI capabilities.

### 🛠️ Systems included
* **Knowledge Graph System**
    * concept dependency graph
    * mastery graph
    * research graph
* **Hybrid GraphRAG**
    * vector search
    * graph traversal
    * multi-hop reasoning
* **Burnout Prediction**
    * **Models:** XGBoost, Random Forest, LightGBM
    * **Inputs:** pomodoro logs, study hours, deadline density
    * **Output:** Burnout Risk Score
* **Reinforcement Learning Scheduler**
    * **State:** mastery, deadlines, fatigue
    * **Action:** schedule study session
    * **Reward:** higher quiz scores, reduced burnout
* **Explainable AI Dashboard**
    * SHAP explanations
    * prediction transparency

**🎯 Result of Phase 5**
* NeuroLearn becomes an Autonomous Student Intelligence System.
