# SentinelOps — System Architecture

## Architecture Philosophy

Event-driven, modular, horizontally scalable. Each layer is independently testable and demoable. All external integrations have mock/simulation fallbacks so the demo never fails.

---

## High-Level Architecture Diagram (Text)

```
┌─────────────────────────────────────────────────────────────────┐
│                        SENTINELOPS SYSTEM                        │
│                                                                   │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────┐   │
│  │  DATA        │    │  ANALYSIS    │    │  LLM ROOT CAUSE   │   │
│  │  INGESTION   │───▶│  ENGINE      │───▶│  INTELLIGENCE     │   │
│  │  LAYER       │    │              │    │                   │   │
│  └─────────────┘    └──────────────┘    └───────────────────┘   │
│         │                  │                       │              │
│         ▼                  ▼                       ▼              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              DECISION INTELLIGENCE DASHBOARD             │    │
│  │  (Risk Heatmap | CI Analytics | Root Cause | KPIs)      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Data Ingestion

### Sources
- **GitHub API** — commits, PRs, CI run status, code diffs
- **GitHub Actions** — workflow logs, build artifacts, test results
- **Docker** — build logs (simulated if needed)
- **Cloud Logs** — simulated CloudWatch/GCP log stream
- **Test Coverage** — Jest/pytest coverage report parsing

### Mechanism
- **GitHub Webhooks** → FastAPI endpoint → Redis queue → Celery worker
- **Polling fallback** for demo reliability (GitHub API every 30s)
- Event types handled:
  - `push` — triggers static risk analysis
  - `pull_request` — triggers merge risk scoring
  - `workflow_run` — triggers CI pattern analysis
  - `workflow_job` — captures step-level logs

### Data Models (Postgres)
```
Repository { id, name, url, risk_score, last_analyzed }
PullRequest { id, repo_id, title, author, lines_changed, file_types, risk_probability, status }
CIRun { id, repo_id, pr_id, status, duration_ms, started_at, finished_at, log_text }
Incident { id, ci_run_id, error_block, root_cause_json, suggested_fix, similarity_score }
LogEmbedding { id, ci_run_id, embedding_vector, cluster_id }
```

---

## Layer 2: Analysis Engine

### Module A: Static Risk Analyzer
**Input:** PR metadata + code diff
**Output:** Risk probability (0.0 – 1.0) + risk factors list

Scoring factors:
- Lines changed (>500 = high risk)
- File types changed (config files = +0.2, test files = -0.1)
- Author's historical failure rate
- PR size relative to repo average
- Dependency file changes (`package.json`, `requirements.txt`, `go.mod`)
- Number of files touched
- Code complexity delta (via radon for Python)

```python
# Risk score formula
risk_score = (
  lines_weight * normalize(lines_changed) +
  file_type_weight * file_type_risk_score +
  author_weight * author_failure_rate +
  dependency_weight * has_dependency_changes +
  complexity_weight * complexity_delta
)
```

### Module B: CI Pattern Analyzer
**Input:** CI run logs + historical CI data
**Output:** Anomaly flags + failure cluster ID

Steps:
1. Extract log text from GitHub Actions API
2. Parse log into structured segments (steps, errors, warnings)
3. Detect anomalous build time (>2 std deviations from mean)
4. Detect flaky test signatures (same test failing non-deterministically)
5. Embed log using SentenceTransformers → `all-MiniLM-L6-v2`
6. Cluster using DBSCAN or cosine similarity against stored embeddings
7. Return: cluster_id, similarity to nearest known incident, anomaly_flags

### Module C: ML Predictive Model
**Algorithm:** Logistic Regression (scikit-learn) — simple, explainable, fast to train
**Purpose:** Demonstrate system thinking, not ML research

```python
# Feature vector per PR
features = [
    lines_changed,          # int
    num_files_changed,      # int
    has_config_changes,     # bool (0/1)
    has_test_changes,       # bool (0/1)  
    author_failure_rate,    # float (0-1)
    pr_age_hours,           # int
    is_large_pr,            # bool (>500 lines)
    dependency_changes,     # bool
    complexity_score,       # float
    time_since_last_deploy  # int (hours)
]
# Output: probability of CI failure (0.0 - 1.0)
```

Training data: synthetic dataset of 500+ historical PRs with outcomes (generated for demo).

---

## Layer 3: LLM Root Cause Intelligence

### Pipeline (triggered on CI failure)

```
CI Failure Detected
       │
       ▼
1. Parse raw log → extract error block (last N lines before failure)
       │
       ▼
2. Retrieve PR diff from GitHub API (files changed)
       │
       ▼
3. Fetch similar past incidents from embedding store
       │
       ▼
4. Build structured prompt → send to OpenAI GPT-4o
       │
       ▼
5. Parse JSON response → store in Postgres
       │
       ▼
6. Push to dashboard via WebSocket
```

### LLM Prompt Template

```
You are SentinelOps, an expert DevOps root cause analyzer.

A CI pipeline has failed. Analyze the following and respond in JSON only.

## Failed CI Log (last 50 lines):
{error_log_block}

## Code Diff (files changed in this PR):
{code_diff}

## Similar Past Incidents:
{similar_incidents}

## Required JSON Response Format:
{
  "root_cause": "Brief explanation of what caused the failure",
  "responsible_files": ["file1.py", "file2.js"],
  "error_category": "dependency|syntax|test|config|runtime|network",
  "confidence": 0.0-1.0,
  "suggested_fix": "Specific code or config change to fix this",
  "fix_diff": "--- a/file.py\n+++ b/file.py\n...",
  "risk_if_unresolved": "What happens if this isn't fixed",
  "estimated_fix_time": "5 minutes|1 hour|half day"
}
```

### Response Handling
- Parse JSON response
- Store in `Incident` table
- Render on dashboard with syntax-highlighted diff
- Enable "Apply Patch Simulation" button

---

## Layer 4: Decision Intelligence Dashboard

See `03_FRONTEND_SPEC.md` for full UI specification.

**Real-time updates via WebSocket** — dashboard auto-refreshes when new incidents detected.

---

## Data Flow Summary

```
GitHub Event
    → Webhook POST /api/webhooks/github
    → Redis Queue (event-driven)
    → Celery Worker picks up task
    → Runs Static Risk Analysis
    → Runs CI Pattern Analysis (if workflow_run)
    → Stores results in Postgres
    → Triggers LLM analysis (if failure)
    → WebSocket broadcast to frontend
    → Dashboard updates in real time
```

---

## Scalability Design (for Judges)

- **Horizontal scaling**: Celery workers scale independently
- **Multi-repo**: Each repo is a separate entity; system supports unlimited repos
- **SaaS model**: Each org gets isolated data namespace
- **Plugin architecture**: New CI providers (CircleCI, Jenkins) add as adapters
- **SOC2 readiness**: All secrets in env vars, audit logging, no PII stored in logs
- **Future**: Kubernetes deployment, per-worker autoscaling, S3 log archival

---

## Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Frontend | Next.js 14 + TypeScript | SSR, API routes, performance |
| Styling | Tailwind CSS | Rapid premium UI |
| Charts | Recharts | React-native charting |
| Animation | Framer Motion | Enterprise polish |
| Graph Viz | React Flow | Incident memory graph |
| Backend | FastAPI (Python) | Async, fast, OpenAPI auto-docs |
| Task Queue | Celery + Redis | Event-driven background processing |
| Database | PostgreSQL | Relational data, complex queries |
| Cache | Redis | Queue + result caching |
| ML | scikit-learn | Logistic regression predictor |
| Embeddings | SentenceTransformers | Log similarity search |
| LLM | OpenAI GPT-4o | Root cause analysis |
| Deployment | Vercel (frontend) + Render (backend) | Fast, free tier |
| Containers | Docker + Docker Compose | Local dev consistency |
