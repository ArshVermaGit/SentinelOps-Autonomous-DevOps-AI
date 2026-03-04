# 🛡️ SentinelOps

> **AI-Powered DevOps Co-Pilot**  
> Built by **Arsh Verma** — Bringing intelligence to the dev pipeline.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production--Ready-emerald?style=for-the-badge)](#)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)

SentinelOps is an **AI-powered DevOps co-pilot** that helps developers understand their delivery pipelines better. It stops the "fail-react" loop by predicting risks at the PR gate and explaining CI/CD failures in plain English.

---

- 📂 **Repo Manager & Sync**: Link local repos, auto-detect changes, run health checks, and push to GitHub from one dashboard.
- 🎭 **Autonomous Gatekeeper**: Reports risk-based commit statuses directly to GitHub to block unsafe merges. [Setup Guide](./GATEKEEPER_SETUP.md)
- 🧪 **Digital Twin Simulation**: Monte Carlo simulations (1,000 iterations) to predict deployment stability.
- 🧠 **Automated Root Cause**: LLM-powered log analysis provides natural language explanations.
- 🔍 **Similarity Search**: Matches new failures against historical incident patterns.

---

## 🎯 Problem

Every engineering team suffers from the same pain:

- CI failures that alert you **after** the damage is done
- Raw logs with **no context** — hours of manual debugging
- PRs that look fine but carry hidden risk
- The same incidents repeating because patterns go unrecognized

**Last month, a typical engineering team loses 12+ hours to CI failures alone.**

---

## 💡 The Solution

SentinelOps is a **real-time engineering insights system** that:

| Feature                          | Description                                                              |
| -------------------------------- | ------------------------------------------------------------------------ |
| 📂 **Repo Manager & Sync**       | Link repos, auto-detect changes, health checks, one-click push to GitHub |
| 🎭 **GitHub Gatekeeper**         | Reports `success`/`failure` to GitHub to block risky PRs                 |
| 🧪 **Digital Twin Engine**       | Runs 1K Monte Carlo iterations to simulate deployment reliability        |
| 🧠 **LLM Root Cause Analysis**   | OpenAI explains _why_ the CI failed + suggests a patch diff              |
| 🔍 **Failure Similarity Search** | Vectorized search: "95% similar to Incident #234 — memory leak pattern"  |
| 📊 **CI Health Analytics**       | Build trends, anomaly detection, and "System Pulse" score                |

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
docker compose up -d
```

### 4. Start the frontend

```bash
cd sentinelops-frontend
npm install
npm run dev
```

### 5. Access the application

- **Dashboard:** http://localhost:3000/dashboard
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

---

## 📂 Real-World Workflow

1. **Dashboard:** See your aggregate system pulse.
2. **Repo Manager:** Link your local repository folders.
3. **Local Sandbox:** Real-time risk detection as you code.
4. **PR Gatekeeper:** AI-scored risk profiles for every change.

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
    │   ├── repositories/       # Repo Manager & Sync
    │   ├── pull-requests/      # PR gatekeeper
    │   └── analytics/          # Engineering insights
    ├── components/             # Reusable UI components
    ├── hooks/                  # Custom React hooks (useRepoManager, etc.)
    └── lib/                    # API client + utilities
```

</div>

## 📱 Connect with Me

I'd love to hear your feedback or discuss potential collaborations!

<div align="center">

[![GitHub](https://skillicons.dev/icons?i=github)](https://github.com/ArshVermaGit)
[![LinkedIn](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/in/arshvermadev/)
[![Twitter](https://skillicons.dev/icons?i=twitter)](https://x.com/TheArshVerma)
[![Gmail](https://skillicons.dev/icons?i=gmail)](mailto:arshverma.dev@gmail.com)

</div>

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/ArshVermaGit">Arsh Verma</a>
</p>
