# 🚀 SentinelOps Local Setup Guide (Step-by-Step)

Follow these exact steps to get SentinelOps running perfectly on your Mac.

---

## 📋 Prerequisites

- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/) (Make sure it is OPEN and RUNNING).
- **Node.js 18+**: [Download here](https://nodejs.org/).
- **Python 3.11+**: [Download here](https://www.python.org/).

---

## 🛠️ Step 1: Environment Configuration

1. **Backend Environment**:
   Open a terminal in the project root and run:
   ```bash
   cp sentinelops-backend/.env.example sentinelops-backend/.env
   ```
   Now, open `sentinelops-backend/.env` and add your keys:
   - `OPENAI_API_KEY`: Your OpenAI key.
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token.

---

## 🏗️ Step 2: Start the Engine (Docker)

Keep your Docker Desktop open, and run this in your terminal (Root Directory):

```bash
cd sentinelops-backend
docker compose up -d
```

_Wait for all containers (api, worker, postgres, redis) to show "Running" in Docker Desktop._

---

## 🧠 Step 3: Initialize AI Models & Data

Run these commands one by one to train the AI and add the beautiful demo data:

1. **Train the ML Model**:

   ```bash
   docker compose exec api python -m app.ml.train
   ```

2. **Seed Demo Data** (The most important step for the demo):
   ```bash
   docker compose exec api env PYTHONPATH=. python scripts/seed_demo_data.py
   ```

---

## 💻 Step 4: Launch the Dashboard

Open a **NEW terminal window** (keep the other one running) and run:

```bash
cd sentinelops-frontend
npm install
npm run dev
```

---

## 🌐 Step 5: Access the App

- **Dashboard**: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
- **Landing Page**: [http://localhost:3000](http://localhost:3000)

---

### 🎥 Demo Recording Tip:

1. Start at the **Landing Page**.
2. Click **"Enter Dashboard"**.
3. Show the **"PR Gatekeeper"** tab (Red alerts).
4. Show an **"Incident"** (AI Root Cause).
5. Open the **"Analytics"** page.

**Deployment Guide**: If you're ready to go live, use the [Deployment Guide](.gemini/antigravity/brain/07a0e04e-59b4-4c38-97d1-8d33d6a5e23c/deployment_guide.md). 🛡️
