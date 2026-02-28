# 🛠️ SentinelOps Local Setup Guide (The Ultimate Version)

Welcome to **SentinelOps**! This guide will walk you through setting up the project locally from scratch.

---

## 🏗️ 1. Prerequisites

Before you begin, ensure you have the following installed and running:

- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/) (**MUST BE RUNNING**)
- **Node.js 20+**: [Download here](https://nodejs.org/)
- **Python 3.11+**: [Download here](https://www.python.org/)

---

## 🔧 2. Environment Setup

### 📡 Backend Configuration

1. Navigate to the backend directory:
   ```bash
   cd sentinelops-backend
   ```
2. Create your `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in your keys:
   - `OPENAI_API_KEY`: Get one from [OpenAI](https://platform.openai.com/)
   - `GITHUB_TOKEN`: Create a Classic PAT with `repo` scopes [here](https://github.com/settings/tokens)

### 🎨 Frontend Configuration

1. Navigate to the frontend directory:
   ```bash
   cd ../sentinelops-frontend
   ```
2. Create your `.env.local` file:
   ```bash
   cp .env.local.example .env.local
   ```

---

## 🚀 3. Running the Project

### Phase A: Start the Engine (Docker)

In your terminal (from the root or backend folder):

```bash
cd sentinelops-backend
docker compose up -d
```

_Wait ~1 minute for Postgres and Redis to initialize._

### Phase B: Power Up the AI

Run these one-time commands to prep the system:

```bash
# 1. Train the ML Risk Model
docker compose exec api python -m app.ml.train

# 2. Seed the Demo Data (The magic part)
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

- **Landing Page**: [http://localhost:3000](http://localhost:3000)
- **AI Dashboard**: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
- **PR Gatekeeper**: View risk scores for pre-seeded PRs.
- **Incident Explorer**: See AI-explained root causes and simulate fixes.

---

## 🤝 5. Contributing

We love contributions! Please refer to the [templates in .github/](.github/) for bug reports, feature requests, and PRs.

## ☕ Support

If you find this project useful, consider supporting the author:
[Buy Me a Coffee](https://www.buymeacoffee.com/ArshVerma)

---

🛡️ **Built with SentinelOps Decision Intelligence**
