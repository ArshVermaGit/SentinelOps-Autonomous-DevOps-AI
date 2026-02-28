# SentinelOps — Build Order & Implementation Guide

## ⚠️ CRITICAL: Build in This Exact Order

The system is designed so each layer is demoable independently. Never get stuck — always have something to show.

---

## Phase 1: Foundation (Do First — 2 hours)

### Step 1.1 — Backend skeleton
```bash
mkdir sentinelops-backend && cd sentinelops-backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg pydantic-settings alembic redis celery
```

Create files in this order:
1. `app/config.py` — settings
2. `app/database.py` — async engine
3. `app/models/` — all 5 model files
4. `app/main.py` — FastAPI app with CORS
5. `docker-compose.yml` — postgres + redis

**Test:** `docker-compose up -d && uvicorn app.main:app --reload`
**Verify:** http://localhost:8000/docs shows API docs ✅

### Step 1.2 — Frontend skeleton
```bash
npx create-next-app@latest sentinelops-frontend --typescript --tailwind --app
cd sentinelops-frontend
npm install recharts reactflow framer-motion lucide-react axios
```

Create files in this order:
1. `app/layout.tsx` — root layout
2. `components/layout/Sidebar.tsx` — navigation
3. `components/layout/TopBar.tsx` — top bar
4. `app/dashboard/page.tsx` — basic dashboard shell

**Test:** `npm run dev` → http://localhost:3000/dashboard shows sidebar ✅

---

## Phase 2: Core Backend (3 hours)

### Step 2.1 — Database migrations
```bash
alembic init alembic
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### Step 2.2 — Seed demo data
```bash
python scripts/seed_demo_data.py
```
This creates all the data you need for demo. **Do this early.**

### Step 2.3 — Dashboard API endpoints
Build `app/routers/dashboard.py` → `/api/dashboard/summary`, `/api/dashboard/ci-health`, `/api/dashboard/risk-heatmap`

**Test:** http://localhost:8000/api/dashboard/summary returns real data from seeded DB ✅

### Step 2.4 — Risk Analyzer + ML Model
1. Copy `app/services/risk_analyzer.py`
2. Copy `app/ml/synthetic_data.py` + `app/ml/train.py`
3. Run: `python -m app.ml.train`
4. Copy `app/services/ml_predictor.py`

**Test:** `POST /api/analysis/analyze-pr` with sample PR data returns risk score ✅

---

## Phase 3: Dashboard UI (2 hours)

Build in this order — each component independently valuable:

1. `components/dashboard/MetricCard.tsx` → KPI row ✅ (looks great already)
2. `hooks/useDashboard.ts` → fetch from API
3. `components/dashboard/CIHealthChart.tsx` → bar chart of builds ✅ (wow factor)
4. `components/dashboard/RiskHeatmap.tsx` → repo risk ranking ✅
5. `components/dashboard/RecentIncidents.tsx` → incident feed ✅
6. `components/dashboard/LiveActivityFeed.tsx` → simulated live events ✅

**CHECKPOINT: At this point you have a shippable demo. Dashboard with real data, charts, risk heatmap.**

---

## Phase 4: LLM Root Cause (2 hours)

### Step 4.1 — LLM Service
Copy `app/services/llm_service.py`. The `analyze_failure_mock()` function works without an API key.

### Step 4.2 — Incidents endpoints
Copy `app/routers/incidents.py`. Wire up with seeded incident data.

### Step 4.3 — Incident detail page
1. `app/incidents/page.tsx` — list view with risk badges
2. `components/incidents/IncidentCard.tsx` — card component
3. `app/incidents/[id]/page.tsx` — detail page
4. `components/incidents/RootCausePanel.tsx` — the wow factor panel
5. `components/incidents/DiffViewer.tsx` — syntax highlighted diff

**Test:** Navigate to an incident, see AI explanation and diff ✅

---

## Phase 5: Advanced Features (2 hours)

### Step 5.1 — Self-Healing Simulation
Copy `app/routers/simulation.py`. This is pure Python, no external dependencies.
Build `components/incidents/SimulationModal.tsx`.

**Test:** Click "Simulate Fix" → see animated steps → success/failure result ✅

### Step 5.2 — PR Risk Gatekeeper
1. Copy `app/routers/pull_requests.py`
2. `app/pull-requests/page.tsx` — PR list sorted by risk
3. `components/pull-requests/PRRiskCard.tsx` — with traffic light

### Step 5.3 — Celery Workers + Webhooks
Copy `app/workers/tasks.py` and `app/workers/celery_app.py`.
Copy `app/routers/webhooks.py`.

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

### Step 5.4 — WebSocket Real-time
Add WebSocket endpoint to `app/main.py`.
Build `hooks/useWebSocket.ts`.
Update dashboard to respond to WebSocket events.

---

## Phase 6: Polish (1 hour)

### Step 6.1 — Incident Memory Graph
Copy `components/graph/IncidentMemoryGraph.tsx`.
Add `app/analytics/page.tsx` with incident graph embedded.

### Step 6.2 — Analytics Page
Copy `app/analytics/page.tsx` with MTTR and engineering insights.

### Step 6.3 — Final polish
- Add Framer Motion page transitions
- Add loading skeletons
- Test all pages on mobile viewport
- Ensure all numbers look realistic
- Add `RealTimeDot.tsx` pulsing indicator to TopBar

---

## Phase 7: Deployment (30 minutes)

### Frontend — Vercel
```bash
cd sentinelops-frontend
npx vercel --prod
# Set env: NEXT_PUBLIC_API_URL=https://your-backend.render.com/api
```

### Backend — Render
1. Push to GitHub
2. Create new Web Service on render.com → connect repo → set env vars
3. Create Background Worker for Celery
4. Add PostgreSQL and Redis databases

---

## Demo Mode Checklist

Before recording your video, verify:
- [ ] `seed_demo_data.py` has been run — DB has data
- [ ] Dashboard loads with real numbers (not zeros)
- [ ] CI Health Chart shows 30 days of build data
- [ ] At least 3 open incidents visible
- [ ] Incident #1 has LLM root cause and diff
- [ ] Simulation modal works (mock mode is fine)
- [ ] PR Risk Gatekeeper shows 🔴 risky PR at top
- [ ] Incident Memory Graph renders with connections
- [ ] Analytics page shows MTTR metrics
- [ ] WebSocket live dot is pulsing in top bar

---

## If You Run Out of Time

**Minimum viable demo (4-5 hours of work):**
1. Backend: seed data + dashboard API + incidents API
2. Frontend: Dashboard (metrics + chart + heatmap) + Incidents list + Incident detail

**This alone is enough for a strong submission** if the UI looks professional and the AI root cause panel is impressive.

Do NOT try to build everything poorly. Build the core beautifully.

---

## Common Issues and Fixes

**"asyncpg not found":**
```bash
pip install asyncpg
```

**"Database connection refused":**
```bash
docker-compose up -d  # Make sure postgres is running
```

**"OpenAI API key not set":**
The code falls back to `analyze_failure_mock()` automatically. Demo works without API key.

**"CORS error in browser":**
Make sure `allow_origins=["*"]` is in FastAPI CORS middleware.

**"Recharts not rendering":**
Wrap chart components in `"use client"` directive and ensure `ResponsiveContainer` has explicit height.

**"ReactFlow import error":**
```bash
npm install reactflow
# Import: import ReactFlow from "reactflow" (default import)
```

---

## Environment Variables Summary

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/sentinelops
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...        # Optional — mock fallback works
GITHUB_TOKEN=ghp_...          # Required for live GitHub integration
GITHUB_WEBHOOK_SECRET=...     # Required for webhook validation
DEBUG=true
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

---

## File Creation Commands

Run these to create the project skeleton instantly:

```bash
# Backend
mkdir -p sentinelops-backend/app/{models,schemas,routers,services,workers,ml,utils}
mkdir -p sentinelops-backend/scripts
mkdir -p sentinelops-backend/tests
touch sentinelops-backend/app/__init__.py
touch sentinelops-backend/app/models/__init__.py
touch sentinelops-backend/app/schemas/__init__.py
touch sentinelops-backend/app/routers/__init__.py
touch sentinelops-backend/app/services/__init__.py
touch sentinelops-backend/app/workers/__init__.py
touch sentinelops-backend/app/ml/__init__.py
touch sentinelops-backend/app/utils/__init__.py

# Frontend
npx create-next-app@latest sentinelops-frontend --typescript --tailwind --app --no-eslint
cd sentinelops-frontend
mkdir -p app/{dashboard,incidents,repositories,pull-requests,analytics}
mkdir -p components/{layout,dashboard,incidents,pull-requests,graph,ui}
mkdir -p {hooks,lib,types}
npm install recharts reactflow framer-motion lucide-react axios clsx tailwind-merge
```
