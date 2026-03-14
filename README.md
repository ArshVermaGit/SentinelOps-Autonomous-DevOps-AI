# 🛡️ SentinelOps

> **AI-Powered DevOps Co-Pilot**  
> Built by **Arsh Verma** — Bringing intelligence to the dev pipeline.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production--Ready-emerald?style=for-the-badge)](#)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)

**SentinelOps** is an autonomous, AI-powered DevOps co-pilot that helps developers understand their delivery pipelines better. It stops the "fail-react" loop by predicting risks at the PR gate and explaining CI/CD failures in plain English.

---

### ✨ Key Features

- 📂 **Repo Manager & Sync**: Link local repos, auto-detect changes, run health checks, and push to GitHub from one unified dashboard.
- 🎭 **Autonomous Gatekeeper**: Reports risk-based commit statuses directly to GitHub to block unsafe merges. [Setup Guide](./GATEKEEPER_SETUP.md)
- 🧪 **Digital Twin Simulation**: Runs Monte Carlo simulations (1,000 iterations) to predict deployment stability before code reaches production.
- 🧠 **Automated Root Cause**: LLM-powered log analysis provides natural language explanations for test/build failures.
- 🔍 **Similarity Search**: Matches new failures against historical incident patterns using vector embeddings.

---

## 🎯 The Problem

Every engineering team suffers from the same pain:
- CI failures that alert you **after** the damage is done.
- Raw logs with **no context** — resulting in hours of manual debugging.
- PRs that look fine but carry hidden structural risks.
- The same incidents repeating because patterns go unrecognized.

**The Reality:** A typical engineering team loses 12+ hours to CI failures and debugging alone every month.

---

## 💡 The Solution

SentinelOps is a **real-time engineering insights system** that mitigates risk entirely:

| Feature | Description |
| :--- | :--- |
| 📂 **Repo Manager & Sync** | Link repos, auto-detect changes, health checks, one-click push to GitHub. |
| 🎭 **GitHub Gatekeeper** | Reports `success`/`failure` to GitHub to block risky PRs autonomously. |
| 🧪 **Digital Twin Engine** | Runs 1K Monte Carlo iterations to simulate deployment reliability. |
| 🧠 **LLM Root Cause Analysis** | OpenAI explains *why* the CI failed + suggests a patch diff. |
| 🔍 **Failure Similarity Search**| Vectorized search: "95% similar to Incident #234 — memory leak pattern". |
| 📊 **CI Health Analytics** | Build trends, anomaly detection, and "System Pulse" health score. |

---

## 🛠️ Tech Stack

**Frontend:** Next.js 14 · TypeScript · Tailwind CSS · Recharts · React Flow · Framer Motion  
**Backend:** FastAPI (Python) · Celery · PostgreSQL · Redis · WebSockets  
**AI/ML:** OpenAI GPT-4o · scikit-learn (Logistic Regression) · SentenceTransformers  
**Infrastructure:** Docker · Docker Compose  

For a deep dive into how these systems interact, see our **[Architecture Deep Dive](./ARCHITECTURE.md)**.

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

*Note: For the ultimate local setup utilizing Docker for databases and workers, see the [Detailed Setup Guide](./SETUP.md).*

### 3. Start Developing

Start both the frontend and backend with a single command:

```bash
make dev
```

- **Dashboard:** [http://localhost:3000](http://localhost:3000)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 📂 Real-World Workflow

1. **Dashboard:** See your aggregate system pulse at a glance.
2. **Repo Manager:** Link your local repository folders.
3. **Local Sandbox:** Get real-time risk detection as you code.
4. **PR Gatekeeper:** Receive AI-scored risk profiles for every upstream change.

---

## 📁 Project Structure

```text
sentinelops/
├── sentinelops-backend/        # FastAPI Python backend
│   ├── app/
│   │   ├── api/                # REST endpoints
│   │   ├── core/               # Configuration & DB
│   │   ├── ml/                 # Risk analyzer & embeddings
│   │   ├── models/             # SQLAlchemy DB schemas
│   │   └── services/           # LLM, Digital Twin, Gatekeeper
│   ├── scripts/                # Seed data & utilities
│   └── tests/                  # Pytest test suite
│
├── sentinelops-frontend/       # Next.js 14 frontend
│   ├── app/
│   │   ├── dashboard/          # Main dashboard
│   │   ├── incidents/          # Incident explorer
│   │   ├── repositories/       # Repo Manager & Sync
│   │   ├── pull-requests/      # PR gatekeeper
│   │   └── analytics/          # Engineering insights
│   ├── components/             # Reusable UI UI
│   ├── hooks/                  # Custom React hooks
│   └── lib/                    # API client + utilities
│
├── Makefile                    # Standardized tooling
├── README.md                   # You are here
├── SETUP.md                    # Detailed Docker setup
└── ARCHITECTURE.md             # Theoretical overview
```

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
