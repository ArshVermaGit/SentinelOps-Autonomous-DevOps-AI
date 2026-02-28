# 🛡️ SentinelOps

> **Autonomous DevOps AI Co-Pilot**  
> Developed by **Arsh Verma** — Engineering Decision Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production--Ready-emerald?style=for-the-badge)](#)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)

SentinelOps is a proactive CI/CD monitoring and self-healing platform that leverages **Machine Learning** to predict build failures and **Generative AI** to automate root-cause analysis. Designed for high-frequency engineering teams, it eliminates the "fail-react" loop by providing predictive intelligence at the Pull Request gate.

---

## 🚀 Key Capabilities

- **🔮 Predictive Risk Scoring**: ML-based auditing of PRs before merge using a custom Logistic Regression model.
- **🧠 Automated Root Cause**: LLM-powered log analysis provides natural language explanations and patch suggestions.
- **🔍 Similarity Search**: Uses SentenceTransformers to match new failures against historical incident patterns.
- **⚡ Self-Healing Sandbox**: Simulates AI-suggested fixes in a containerized environment to verify outcomes.
- **📊 Engineering Analytics**: Real-time visibility into MTTR, deployment stability, and pipeline health.

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

| Feature                          | Description                                                       |
| -------------------------------- | ----------------------------------------------------------------- |
| 🔮 **Merge Risk Gatekeeper**     | Scores every PR before merge: 🟢 Safe / 🟡 Caution / 🔴 High Risk |
| 🧠 **LLM Root Cause Analysis**   | OpenAI explains _why_ the CI failed + suggests a patch diff       |
| 🔍 **Failure Similarity Search** | "95% similar to Incident #234 — memory leak pattern"              |
| ⚡ **Self-Healing Simulation**   | Apply AI patch in sandbox, rerun tests, see predicted outcome     |
| 📊 **CI Health Analytics**       | Build trends, anomaly detection, flaky test identification        |
| 🕸️ **Incident Memory Graph**     | Interactive PR → Commit → Author → Failure relationship graph     |

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

### 4. Train the ML model

```bash
docker compose exec api python -m app.ml.train
```

### 5. Seed demo data

```bash
docker compose exec api python scripts/seed_demo_data.py
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
