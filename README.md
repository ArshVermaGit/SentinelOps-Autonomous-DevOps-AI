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
git clone https://github.com/ArshVermaGit/SentinelOps-Autonomous-DevOps-AI
cd SentinelOps
```

### 2. Standardized Setup

We provide a `Makefile` to simplify development. Run the following command to install all dependencies and configure your environment:

```bash
make setup
```

This will:

- Install root dependencies.
- Setup the frontend (install packages, create `.env.local`).
- Setup the backend (create virtual environment, install requirements, create `.env`).

### 3. Start Developing

You can start both the frontend and backend with a single command:

```bash
make dev
```

- **Dashboard:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

---

## 🤝 Contributing

We love contributions! SentinelOps is built to be modular and easy to extend.

1. **Check the [Contributing Guide](./CONTRIBUTING.md)** for architecture details and coding standards.
2. **Standard Commands:**
   - `make lint`: Run all linters.
   - `make format`: Auto-format code.
   - `make test`: Run the test suite.
   - `make build`: Production build.

---

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
## 🚀 Backend Development

We recommend using the root `Makefile` for a consistent experience across the project.

- `make setup`: Setup the backend environment (venv, dependencies).
- `make dev`: Start the FastAPI server.
- `make lint`: Run flake8.
- `make format`: Run black and isort.
- `make test`: Run pytest.
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
