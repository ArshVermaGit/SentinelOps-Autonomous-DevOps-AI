# SentinelOps 🛡️

### Autonomous DevOps AI Co-Pilot — Engineering Decision Intelligence

> Built for **DevDash 2026** Hackathon | "Code the Tomorrow"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 Problem

Every engineering team suffers from the same pain:
- CI failures that alert you **after** the damage is done
- Raw logs with **no context** — hours of manual debugging
- PRs that look fine but carry hidden risk
- The same incidents repeating because patterns go unrecognized

**Last month, a typical engineering team loses 12+ hours to CI failures alone.**

---

## 💡 Solution

SentinelOps is a **real-time AI engineering intelligence system** that:

| Feature | Description |
|---------|-------------|
| 🔮 **Merge Risk Gatekeeper** | Scores every PR before merge: 🟢 Safe / 🟡 Caution / 🔴 High Risk |
| 🧠 **LLM Root Cause Analysis** | OpenAI explains *why* the CI failed + suggests a patch diff |
| 🔍 **Failure Similarity Search** | "95% similar to Incident #234 — memory leak pattern" |
| ⚡ **Self-Healing Simulation** | Apply AI patch in sandbox, rerun tests, see predicted outcome |
| 📊 **CI Health Analytics** | Build trends, anomaly detection, flaky test identification |
| 🕸️ **Incident Memory Graph** | Interactive PR → Commit → Author → Failure relationship graph |

---

## 🏗️ Architecture

```
GitHub Webhooks → FastAPI → Redis Queue → Celery Workers
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                        Risk Analyzer   CI Analyzer      LLM Engine
                        (Logistic       (Embeddings +    (OpenAI GPT-4o)
                         Regression)     DBSCAN)
                              │               │               │
                              └───────────────┴───────────────┘
                                              │
                                       PostgreSQL + Redis
                                              │
                                    Next.js Dashboard
                                    (WebSocket real-time)
```

---

## 🛠️ Tech Stack

**Frontend:** Next.js 14 · TypeScript · Tailwind CSS · Recharts · React Flow · Framer Motion

**Backend:** FastAPI (Python) · Celery · PostgreSQL · Redis · WebSockets

**AI/ML:** OpenAI GPT-4o · scikit-learn (Logistic Regression) · SentenceTransformers

**Infrastructure:** Docker · Docker Compose · Vercel · Render

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- OpenAI API Key
- GitHub Personal Access Token

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sentinelops
cd sentinelops
```

### 2. Configure environment variables
```bash
cp sentinelops-backend/.env.example sentinelops-backend/.env
# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-...
# GITHUB_TOKEN=ghp_...
```

### 3. Start backend services
```bash
cd sentinelops-backend
docker-compose up -d
```

### 4. Train the ML model
```bash
docker-compose exec api python -m app.ml.train
```

### 5. Seed demo data
```bash
docker-compose exec api python scripts/seed_demo_data.py
```

### 6. Start the frontend
```bash
cd sentinelops-frontend
npm install
npm run dev
```

### 7. Access the application
- **Dashboard:** http://localhost:3000/dashboard
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

---

## 📁 Project Structure

```
sentinelops/
├── sentinelops-backend/        # FastAPI Python backend
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── routers/            # API route handlers
│   │   ├── services/           # Business logic
│   │   ├── workers/            # Celery background tasks
│   │   └── ml/                 # ML model training + inference
│   ├── scripts/
│   │   └── seed_demo_data.py   # Demo data seeder
│   ├── docker-compose.yml
│   └── requirements.txt
│
└── sentinelops-frontend/       # Next.js 14 frontend
    ├── app/
    │   ├── dashboard/          # Main dashboard
    │   ├── incidents/          # Incident explorer
    │   ├── repositories/       # Risk heatmap
    │   ├── pull-requests/      # PR gatekeeper
    │   └── analytics/          # Engineering insights
    ├── components/             # Reusable UI components
    ├── hooks/                  # Custom React hooks
    └── lib/                    # API client + utilities
```

---

## 🎬 Demo Script (Follow This for Video)

**Narrative: "Last month, our CI failed 17 times, costing 12 engineering hours. With SentinelOps, this is what that would look like."**

1. **Open Dashboard** → Show live metrics: 87% success rate, 3 open incidents, risk heatmap
2. **Navigate to PR Gatekeeper** → Show the "Migrate auth to JWT" PR with 🔴 91% failure risk
3. **Show Risk Factors** → "Large change: 1090 lines, dependency changes, no test coverage"
4. **Merge the PR** → CI run triggers → **Dashboard auto-updates** → Failure detected!
5. **Open the Incident** → AI Root Cause Panel: "JWT secret not configured in test environment"
6. **Show the Diff** → Exact fix shown in unified diff format
7. **Click "Simulate Fix"** → Watch sandbox steps run → "CI pipeline would PASS — 94% confidence"
8. **Navigate to Incident Memory Graph** → Show "95% similar to Incident #8 from 3 weeks ago"
9. **Close with Analytics page** → "MTTR down 23% with SentinelOps. Deployment stability: 87%."

**Demo runtime: ~3 minutes. Keep it tight.**

---

## 🔌 GitHub Webhook Setup

1. Go to your GitHub repo → Settings → Webhooks → Add webhook
2. **Payload URL:** `https://your-backend.render.com/api/webhooks/github`
3. **Content type:** `application/json`
4. **Events:** Pull requests, Workflow runs
5. **Secret:** Set `GITHUB_WEBHOOK_SECRET` in your `.env`

---

## 🧪 Running Tests

```bash
cd sentinelops-backend
pytest tests/ -v
```

---

## 🗺️ Roadmap

- [ ] **v1.1:** CircleCI and Jenkins adapter plugins
- [ ] **v1.2:** Slack/Teams notification integration
- [ ] **v2.0:** Autonomous PR comment posting with risk report
- [ ] **v2.1:** Multi-organization SaaS with isolated namespaces
- [ ] **v3.0:** Kubernetes deployment with per-worker autoscaling
- [ ] **v3.1:** SOC2 compliance mode with audit logging

---

## 👥 Team

Built for DevDash 2026 — "Code the Tomorrow"

---

## 📜 License

MIT License — see LICENSE file for details

---

## 🤖 AI Disclosure

This project uses:
- **OpenAI GPT-4o** for root cause analysis and fix suggestions
- **SentenceTransformers (all-MiniLM-L6-v2)** for log embedding and similarity search
- **scikit-learn** for CI failure prediction
- **Claude (Anthropic)** assisted with initial architecture planning

Per DevDash 2026 rules, all AI model usage is disclosed above.
# SentinelOps-Autonomous-DevOps-AI
