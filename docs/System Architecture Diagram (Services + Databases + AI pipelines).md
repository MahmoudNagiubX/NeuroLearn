## 🏗️ System Architecture
Here is the high-level microservices and data flow architecture Diagram (All Phases) for NeuroLearn:

```mermaid
flowchart TB
    U[User] --> FE[Frontend Web App\nNext.js/React]
    FE --> GW[API Gateway / BFF\nFastAPI or Node]

    GW --> AUTH[Auth Service\nJWT + Refresh]
    GW --> CORE[Core App Service\nTasks/Planner/Notes/Pomodoro]
    GW --> FILE[File Service\nUploads + Storage]
    GW --> ANA[Analytics Service\nDashboards + Aggregations]

    %% AI Services
    GW --> RAG[RAG Service\nQ&A + Summaries]
    GW --> ING[Ingestion Service\nParse/Chunk/Embed]
    GW --> KT[Knowledge Tracing Service\nBKT/IRT/Bandits]
    GW --> QUIZ[Quiz Service\nGenerator + Attempts]
    GW --> CODE[Code Analyzer Service\nAST + Eval]
    GW --> RES[Research Assistant Service\nPaper parsing + compare]
    GW --> KG[Knowledge Graph Service\nConcept Graph + Mastery Graph]
    GW --> PRED[Prediction Service\nBurnout/Readiness]
    GW --> SCHED[Scheduler Service\nBandit/RL planning]

    %% Datastores
    AUTH --> PG[(PostgreSQL\nUsers/Accounts)]
    CORE --> PG2[(PostgreSQL\nTasks/Notes/Sessions)]
    ANA --> PG2
    FILE --> OBJ[(Object Storage\nS3/MinIO)]
    ING --> OBJ
    RAG --> VDB[(Vector DB\nFAISS/Qdrant/Pinecone)]
    KG --> GDB[(Graph DB\nNeo4j)]
    KT --> PG3[(PostgreSQL\nMastery/Attempts)]
    QUIZ --> PG3
    CODE --> PG4[(PostgreSQL\nCode submissions)]
    RES --> PG5[(PostgreSQL\nPapers/Metadata)]

    %% Infra
    GW --> REDIS[(Redis Cache)]
    ING --> MQ[(Message Broker\nRabbitMQ/Kafka)]
    FILE --> MQ
    MQ --> ING
    MQ --> RAG
    MQ --> ANA
```
### How to read this:
- The API Gateway/BFF is the only thing the frontend talks to.
- Every major capability is a service behind it (even if Phase 1 you run them inside one codebase).

---

## 🏗️ Phase-by-Phase: "What Exists When"

### 📍 Phase 1 (MVP Productivity)
**Strategy:** Run as one Core API + Postgres (and optional Redis).
* **Services active:** API Gateway, Auth, Core App, Basic Analytics.
* **Databases:** PostgreSQL (required), Redis (optional), Object storage (optional).
* ✅ **Deployment:** Deployable with **Docker Compose**.

### 🤖 Phase 2 (Vector RAG Study Assistant)
**Strategy:** Add AI ingestion + RAG.
* **Services added:** File Service, Ingestion Service, RAG Service, Vector DB.
* **Databases added:** Object storage (S3/MinIO), Vector DB (Qdrant/FAISS).

### 📈 Phase 3 (Adaptive Learning Engine)
**Strategy:** Add quiz attempts + mastery.
* **Services added:** Quiz Service, Knowledge Tracing Service (BKT), Mastery Dashboard.
* **Databases added:** Postgres tables for attempts/mastery + event logs.

### 🔬 Phase 4 (Research + Code Intelligence)
**Strategy:** Add research paper parsing and code analysis.
* **Services added:** Research Assistant Service, Code Analyzer Service.

### 🌌 Phase 5 (Advanced Intelligence)
**Strategy:** Add graph + prediction + RL.
* **Services added:** Knowledge Graph Service (Neo4j), Hybrid GraphRAG (RAG + KG), Prediction Service (burnout/readiness), Scheduler Service (bandit → RL), Explainability in Analytics

---

## 🗄️ Core Data Stores (What goes where)

### 🐘 PostgreSQL (Source of truth)
* **Phase 1-2:** Users, subjects/courses, tasks, notes, sessions, pomodoro logs.
* **Phase 3-4:** Quiz attempts, mastery probabilities, paper metadata, code submission metadata.

### 📦 Object Storage (S3/MinIO)
* **Content:** PDFs, slides, research papers, images, note attachments.

### 🔍 Vector DB (FAISS/Qdrant/Pinecone)
* **Embeddings:** Document chunk embeddings (study assistant).
* **Future:** Note embeddings (later), Paper embeddings (research assistant).

### 🕸️ Neo4j (Phase 5)
* **Graphs:** Concept dependency graph, paper citation/method graph.
* **Personalization:** Mastery graph (user → concept → mastery_prob).

### ⚡ Redis
* **Operations:** Sessions, rate limiting, caching RAG results, caching mastery summaries.

### 📩 Message Broker (RabbitMQ/Kafka)
* **Async Pipelines:** * Upload triggers ingestion
    * Ingestion triggers embedding
    * Embedding triggers indexing
* **Background Jobs:** Analytics aggregation jobs.

---

## 🤖 AI Pipelines (Exact Data Flow)
### 1) RAG Ingestion Pipeline (Phase 2)

```mermaid
flowchart LR
  UP[Upload PDF/Slides] --> FS[File Service -> S3/MinIO]
  FS --> EVT[Publish Event: file_uploaded]
  EVT --> PARSE[Ingestion: Parse Text]
  PARSE --> CHUNK[Chunk + Metadata]
  CHUNK --> EMB[Embedding Model]
  EMB --> VDB[Upsert vectors to Vector DB]
  CHUNK --> PG[(Store chunk metadata in Postgres)]
```
### Key design rule:
Vectors go to Vector DB; chunk metadata + permissions stay in Postgres.

---

### 2) RAG Query Pipeline (Phase 2)
```mermaid
flowchart LR
  Q[User question] --> RAG[RAG Service]
  RAG --> RET[Retrieve Top-k from Vector DB]
  RET --> RERANK[Rerank optional]
  RERANK --> PROMPT[Build grounded prompt with citations]
  PROMPT --> LLM[LLM Inference]
  LLM --> OUT[Answer + citations + confidence]
  OUT --> LOG[Store interaction logs in Postgres]
```

---

### 3) Knowledge Tracing Pipeline (Phase 3)
```mermaid
flowchart LR
  ATT[Quiz attempt submitted] --> QUIZ[Quiz Service]
  QUIZ --> LOG[Store attempt in Postgres]
  LOG --> KT[Knowledge Tracing Service\nBKT update]
  KT --> M[(Update mastery probs per concept)]
  M --> DASH[Mastery Dashboard]
```

---

### 4) Code Analyzer Pipeline (Phase 4)
```mermaid
flowchart LR
  CODEIN[Code submission] --> CA[Code Analyzer]
  CA --> AST[tree-sitter AST parse]
  AST --> TEST[Test runner]
  TEST --> METRICS[Complexity heuristics + quality]
  METRICS --> SAVE[(Postgres)]
  METRICS --> FEED[Optional: feed weakness tags to KT]
```

---

### 5) Research Paper Pipeline (Phase 4)
```mermaid
flowchart LR
  PAPER[Upload paper] --> PARSE[Structured parse]
  PARSE --> EX[Extract: method/dataset/metrics]
  EX --> EMB[Embeddings]
  EMB --> VDB[(Vector DB)]
  EX --> META[(Postgres metadata)]
  EX --> CMP[Compare papers + related work]
```

---

### 5) Hybrid GraphRAG (Phase 5)
```mermaid
flowchart LR
  Q[User question] --> TP[Tool Planner]
  TP -->|fact lookup| VRET[Vector retrieval]
  TP -->|dependency reasoning| GRET[Graph traversal]
  VRET --> MERGE[Evidence Fusion]
  GRET --> MERGE
  MERGE --> LLM[LLM grounded answer]
```

---

## What to Build First

1. DB schema + migrations (subjects, tasks, sessions, notes, pomodoro_logs)
2. Auth + JWT
3. Core endpoints (CRUD)
4. Frontend screens
5. Basic analytics aggregates
6. File upload + storage (bridge to Phase 2)
7. Ingestion worker + vector DB (Phase 2 begins)
