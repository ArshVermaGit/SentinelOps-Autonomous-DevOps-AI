# 🛠️ SentinelOps Local Setup Guide

Welcome to **SentinelOps**! This guide is explicitly designed to get you up and running locally from scratch in under 5 minutes. We use Docker to ensure the setup is completely reproducible and standardized.

> **Note to Hackathon Judges / Evaluators:** We highly recommend following this guide closely. It spins up the heavy AI workers and databases inside Docker, ensuring you don't have to install Redis or PostgreSQL locally.

---

## 🏗️ 1. Prerequisites

Before you begin, ensure you have the following installed and running:

- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/) (**MUST BE RUNNING**)
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Python 3.11+**: [Download here](https://www.python.org/)

---

## 🔧 2. Environment Configuration

### 📡 Backend Configuration

1. Navigate to the backend directory:
   ```bash
   cd sentinelops-backend
   ```
2. Create your `.env` file from the provided template:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in your keys:
   - `OPENAI_API_KEY`: Required for LLM Root Cause Analysis. [Get one from OpenAI](https://platform.openai.com/).
   - `GITHUB_TOKEN`: Required to sync repositories and post commit statuses. Create a Classic PAT with `repo` scopes [here](https://github.com/settings/tokens).

### 🎨 Frontend Configuration

1. Navigate to the frontend directory:
   ```bash
   cd ../sentinelops-frontend
   ```
2. Create your `.env.local` file from the template:
   ```bash
   cp .env.local.example .env.local
   ```

---

## 🚀 3. Running the Project

### Phase A: Start the Core Infrastructure (Docker)

In your terminal (from the `sentinelops-backend` folder):

```bash
docker compose up -d
```

*Wait ~30 seconds for PostgreSQL and Redis to initialize.* This command starts the database, in-memory cache, Celery worker for background AI tasks, and Celery beat for scheduling.

### Phase B: Power Up the AI Models & Demo Data

Run these one-time commands to prep the system with realistic data:

```bash
# 1. Train the Machine Learning Risk Model locally
docker compose exec api python -m app.ml.train

# 2. Seed the Demo Data (This generates mock incidents, risks, and health tiles)
docker compose exec api env PYTHONPATH=. python scripts/seed_demo_data.py
```

### Phase C: Launch the Dashboard

Open a **new terminal tab**:

```bash
cd sentinelops-frontend
npm install
npm run dev
```

---

## 🌐 4. Explore the Features

Take SentinelOps for a spin! Once everything is running, explore these URLs:

- 📊 **Main AI Dashboard**: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)  
  *View aggregate system pulse, build times, and the top-level risk heatmap.*
- 🛡️ **PR Gatekeeper**: [http://localhost:3000/pull-requests](http://localhost:3000/pull-requests)  
  *View dynamic risk scores and logistic regression outputs for pre-seeded PRs.*
- 🚨 **Incident Explorer**: [http://localhost:3000/incidents](http://localhost:3000/incidents)  
  *Select an incident to see AI-explained root causes, Vector Similarity search results, and run Digital Twin latency simulations.*
- ⚙️ **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)  
  *Explore and test the underlying REST endpoints driving the platform.*

---

## 💡 Troubleshooting

- **Redis Connection Errors:** Ensure Docker Desktop is actually running. If containers aren't spinning up, run `docker compose down -v` followed by `docker compose up -d --build`.
- **LLM Expalantions Failing:** Ensure your `OPENAI_API_KEY` is valid and has sufficient credits.
- **Port Conflicts:** The backend binds to `8000` and `5432` (Postgres). The frontend binds to `3000`. Ensure these ports are free.

---

🛡️ **Built with SentinelOps Decision Intelligence**
