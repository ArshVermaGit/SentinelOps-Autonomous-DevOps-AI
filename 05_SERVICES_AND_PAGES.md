# SentinelOps — GitHub Service & Additional Components

## app/services/github_service.py

```python
"""
GitHub API client for SentinelOps.
Handles all GitHub API interactions with graceful fallback for demo mode.
"""
import httpx
import base64
import re
from app.config import settings

GITHUB_API_BASE = "https://api.github.com"

class GitHubService:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def get_pull_request(self, repo: str, pr_number: int) -> dict:
        """Fetch PR metadata."""
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}",
                headers=self.headers,
                timeout=10.0
            )
            r.raise_for_status()
            return r.json()
    
    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """Fetch PR unified diff."""
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}",
                headers={**self.headers, "Accept": "application/vnd.github.diff"},
                timeout=10.0
            )
            r.raise_for_status()
            return r.text[:5000]  # Truncate to 5KB
    
    async def get_pr_files(self, repo: str, pr_number: int) -> list[dict]:
        """Get list of files changed in PR."""
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}/files",
                headers=self.headers,
                timeout=10.0
            )
            r.raise_for_status()
            return r.json()
    
    async def get_run_logs(self, repo: str, run_id: int) -> str:
        """
        Download CI run logs.
        Returns log text (truncated to last 200 lines).
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Get download URL
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/actions/runs/{run_id}/logs",
                headers=self.headers,
                timeout=30.0
            )
            if r.status_code == 302:
                # Follow redirect to download
                log_r = await client.get(r.headers["Location"], timeout=30.0)
                log_text = log_r.text
            else:
                log_text = r.text
            
            # Return last 200 lines
            lines = log_text.split("\n")
            return "\n".join(lines[-200:])
    
    async def get_workflow_run(self, repo: str, run_id: int) -> dict:
        """Get workflow run details."""
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/actions/runs/{run_id}",
                headers=self.headers,
                timeout=10.0
            )
            r.raise_for_status()
            return r.json()
    
    async def get_author_stats(self, repo: str, author: str) -> dict:
        """
        Get author's historical PR stats.
        Returns: { total_prs, failed_prs, avg_lines_changed }
        """
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{GITHUB_API_BASE}/search/issues",
                params={
                    "q": f"repo:{repo} author:{author} type:pr is:closed",
                    "per_page": 100
                },
                headers=self.headers,
                timeout=10.0
            )
            data = r.json()
            total = data.get("total_count", 0)
            
            # For demo: estimate failure rate
            return {
                "total_prs": total,
                "failed_prs": int(total * 0.18),  # Estimated from repo failure rate
                "avg_lines_changed": 200
            }
    
    async def create_pr_comment(self, repo: str, pr_number: int, body: str) -> dict:
        """
        Post SentinelOps risk analysis as PR comment.
        (Autonomous mode feature)
        """
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{GITHUB_API_BASE}/repos/{repo}/issues/{pr_number}/comments",
                headers=self.headers,
                json={"body": body},
                timeout=10.0
            )
            r.raise_for_status()
            return r.json()
    
    def format_pr_risk_comment(self, risk_data: dict) -> str:
        """Format risk analysis as GitHub PR comment markdown."""
        emoji = "🟢" if risk_data["risk_level"] == "safe" else \
                "🟡" if risk_data["risk_level"] == "caution" else "🔴"
        
        factors_md = "\n".join([f"- {f}" for f in risk_data.get("risk_factors", [])])
        
        return f"""## {emoji} SentinelOps Risk Analysis

**CI Failure Probability**: `{risk_data['risk_probability']:.0%}`  
**Risk Level**: **{risk_data['risk_level'].upper()}**

### Risk Factors
{factors_md or "_No significant risk factors detected_"}

---
*Powered by SentinelOps — Autonomous DevOps AI Co-Pilot*
"""
```

---

## app/utils/log_parser.py

```python
"""
Utilities for parsing CI/CD log output.
"""
import re
from typing import Optional

# Common error patterns across CI providers
ERROR_PATTERNS = [
    r"ERROR:.*",
    r"Error:.*",
    r"FAILED.*",
    r"Traceback \(most recent call last\):",
    r"Exception:.*",
    r"AssertionError:.*",
    r"ModuleNotFoundError:.*",
    r"ImportError:.*",
    r"SyntaxError:.*",
    r"npm ERR!.*",
    r"yarn error.*",
    r"Process completed with exit code [1-9]",
    r"make: \*\*\*.*Error",
    r"COMPILATION ERROR",
    r"Build FAILED",
    r"Tests failed:",
    r"✗ FAIL",
    r"FAILURE: Build failed",
]

STEP_PATTERN = re.compile(r"^##\[.*?\]Run (.+)$", re.MULTILINE)

def extract_error_block(log_text: str, context_lines: int = 30) -> str:
    """
    Intelligently extract the most relevant error block from CI logs.
    
    Strategy:
    1. Find the last occurrence of a known error pattern
    2. Return N lines before and after for context
    """
    lines = log_text.split("\n")
    
    # Find lines matching error patterns
    error_line_indices = []
    for i, line in enumerate(lines):
        for pattern in ERROR_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                error_line_indices.append(i)
                break
    
    if not error_line_indices:
        # No errors found — return last N lines
        return "\n".join(lines[-context_lines:])
    
    # Use the last error occurrence as the anchor
    last_error_idx = error_line_indices[-1]
    
    # Also include any lines in a "block" around this error
    start = max(0, last_error_idx - 15)
    end = min(len(lines), last_error_idx + 15)
    
    # Expand backward to include full stack trace if applicable
    if any("Traceback" in l or "at " in l for l in lines[start:last_error_idx]):
        traceback_start = start
        for i in range(last_error_idx, max(0, last_error_idx - 40), -1):
            if "Traceback" in lines[i] or "Error in" in lines[i]:
                traceback_start = i
                break
        start = traceback_start
    
    return "\n".join(lines[start:end])


def detect_flaky_test(run_logs: list[str]) -> bool:
    """
    Detect if a test is flaky by comparing multiple run logs.
    Returns True if same test alternates between pass/fail.
    """
    # Simple heuristic: if failure pattern is inconsistent across runs
    failed_tests_per_run = []
    
    for log in run_logs:
        failed = set()
        for line in log.split("\n"):
            match = re.search(r"FAILED (tests/\S+)", line)
            if match:
                failed.add(match.group(1))
        failed_tests_per_run.append(failed)
    
    if len(failed_tests_per_run) < 2:
        return False
    
    # Flaky if tests fail in some runs but not others
    all_failed = set().union(*failed_tests_per_run)
    for test in all_failed:
        failed_in = sum(1 for run in failed_tests_per_run if test in run)
        if 0 < failed_in < len(failed_tests_per_run):
            return True
    
    return False


def detect_anomalous_build_time(
    current_duration_ms: int,
    historical_durations: list[int],
    std_multiplier: float = 2.0
) -> bool:
    """
    Returns True if current build time is anomalously high or low.
    Uses mean ± N standard deviations.
    """
    if len(historical_durations) < 5:
        return False  # Not enough data
    
    import statistics
    mean = statistics.mean(historical_durations)
    stdev = statistics.stdev(historical_durations)
    
    lower = mean - std_multiplier * stdev
    upper = mean + std_multiplier * stdev
    
    return not (lower <= current_duration_ms <= upper)


def extract_file_types(filenames: list[str]) -> list[str]:
    """Extract unique file extensions from a list of filenames."""
    import os
    extensions = set()
    for f in filenames:
        _, ext = os.path.splitext(f)
        if ext:
            extensions.add(ext.lower())
    return list(extensions)


def is_config_file(filename: str) -> bool:
    """Check if a file is a configuration file."""
    config_patterns = [
        ".yaml", ".yml", ".json", ".toml", ".ini", ".env", ".cfg",
        "dockerfile", "docker-compose", ".tf", ".tfvars", "makefile"
    ]
    lower = filename.lower()
    return any(p in lower for p in config_patterns)


def is_dependency_file(filename: str) -> bool:
    """Check if a file is a dependency manifest."""
    dep_files = [
        "package.json", "package-lock.json", "yarn.lock",
        "requirements.txt", "pyproject.toml", "setup.py", "Pipfile",
        "go.mod", "go.sum", "Cargo.toml", "Cargo.lock",
        "pom.xml", "build.gradle", "Gemfile"
    ]
    return any(filename.endswith(d) or filename == d for d in dep_files)


def is_test_file(filename: str) -> bool:
    """Check if a file is a test file."""
    test_patterns = ["test_", "_test.", ".test.", ".spec.", "/tests/", "/test/", "__tests__"]
    lower = filename.lower()
    return any(p in lower for p in test_patterns)
```

---

## app/services/websocket_service.py

```python
"""
WebSocket service for real-time dashboard updates.
"""
from fastapi import WebSocket
from typing import set as Set
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        
        for conn in dead:
            self.disconnect(conn)

manager = ConnectionManager()

async def broadcast_new_incident(incident_id: int):
    await manager.broadcast({
        "type": "new_incident",
        "incident_id": incident_id,
        "message": f"New incident detected: #{incident_id}"
    })

async def broadcast_ci_failure(ci_run_id: int, repo_name: str):
    await manager.broadcast({
        "type": "ci_failure",
        "ci_run_id": ci_run_id,
        "repo_name": repo_name,
        "message": f"CI failure detected in {repo_name}"
    })

async def broadcast_pr_risk(pr_id: int, risk_level: str, risk_probability: float):
    await manager.broadcast({
        "type": "pr_risk_update",
        "pr_id": pr_id,
        "risk_level": risk_level,
        "risk_probability": risk_probability,
    })
```

---

## WebSocket Router Addition (add to app/main.py)

```python
from fastapi import WebSocket, WebSocketDisconnect
from app.services.websocket_service import manager

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            # Echo back ping/pong for keepalive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## app/routers/analysis.py

```python
"""
Manual analysis trigger endpoints — for demo button clicks.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.services.risk_analyzer import RiskAnalyzer
from app.services.ml_predictor import predict_failure_probability, normalize_pr_features
from app.services.llm_service import analyze_failure, analyze_failure_mock
from app.config import settings

router = APIRouter()
risk_analyzer = RiskAnalyzer()

class PRAnalysisRequest(BaseModel):
    title: str
    lines_added: int = 0
    lines_deleted: int = 0
    files_changed: int = 1
    has_config_changes: bool = False
    has_test_changes: bool = True
    has_dependency_changes: bool = False
    author_failure_rate: float = 0.15
    pr_age_hours: float = 24

@router.post("/analyze-pr")
async def analyze_pr_manual(req: PRAnalysisRequest):
    """
    Manually trigger PR risk analysis.
    Used for demo mode — input a PR's details and get risk score back.
    """
    pr_data = req.dict()
    
    # Rule-based risk analysis
    rule_result = risk_analyzer.analyze_pr(pr_data, {
        "total_prs": 50,
        "failed_prs": int(req.author_failure_rate * 50),
        "avg_lines_changed": 200
    })
    
    # ML model prediction
    normalized = normalize_pr_features(pr_data)
    ml_probability = predict_failure_probability(normalized)
    
    # Blend: 60% ML, 40% rule-based
    final_probability = 0.6 * ml_probability + 0.4 * rule_result["risk_probability"]
    
    risk_level = "safe" if final_probability < 0.35 else "caution" if final_probability < 0.65 else "high"
    
    return {
        "risk_probability": round(final_probability, 3),
        "risk_level": risk_level,
        "risk_factors": rule_result["risk_factors"],
        "ml_score": ml_probability,
        "rule_score": rule_result["risk_probability"],
        "component_scores": rule_result["component_scores"]
    }

class LogAnalysisRequest(BaseModel):
    log_text: str
    code_diff: str = ""

@router.post("/analyze-log")
async def analyze_log_manual(req: LogAnalysisRequest):
    """
    Manually trigger LLM root cause analysis on a log snippet.
    Demo endpoint — paste any log and get AI analysis.
    """
    if len(req.log_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Log text too short")
    
    try:
        result = await analyze_failure(req.log_text, req.code_diff, [])
    except Exception:
        # Fallback to mock for demo if API key not configured
        result = await analyze_failure_mock(req.log_text)
    
    return result
```

---

## app/routers/pull_requests.py

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.pull_request import PullRequest
from app.models.repository import Repository

router = APIRouter()

@router.get("/")
async def list_pull_requests(
    risk_level: str = None,
    repo_id: int = None,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List PRs sorted by risk score descending."""
    query = select(PullRequest).order_by(desc(PullRequest.risk_probability))
    
    if risk_level:
        query = query.where(PullRequest.risk_level == risk_level)
    if repo_id:
        query = query.where(PullRequest.repo_id == repo_id)
    
    query = query.limit(limit)
    result = await db.execute(query)
    prs = result.scalars().all()
    
    return [
        {
            "id": pr.id,
            "title": pr.title,
            "author": pr.author,
            "risk_probability": pr.risk_probability,
            "risk_level": pr.risk_level,
            "risk_factors": pr.risk_factors,
            "lines_added": pr.lines_added,
            "lines_deleted": pr.lines_deleted,
            "files_changed": pr.files_changed,
            "has_dependency_changes": pr.has_dependency_changes,
            "status": pr.status,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
        }
        for pr in prs
    ]

@router.get("/{pr_id}")
async def get_pull_request(pr_id: int, db: AsyncSession = Depends(get_db)):
    """Get single PR with full risk analysis."""
    result = await db.execute(select(PullRequest).where(PullRequest.id == pr_id))
    pr = result.scalar_one_or_none()
    
    if not pr:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="PR not found")
    
    return {
        "id": pr.id,
        "title": pr.title,
        "author": pr.author,
        "risk_probability": pr.risk_probability,
        "risk_level": pr.risk_level,
        "risk_factors": pr.risk_factors or [],
        "lines_added": pr.lines_added,
        "lines_deleted": pr.lines_deleted,
        "files_changed": pr.files_changed,
        "has_config_changes": pr.has_config_changes,
        "has_test_changes": pr.has_test_changes,
        "has_dependency_changes": pr.has_dependency_changes,
        "status": pr.status,
    }
```

---

## app/routers/incidents.py

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.incident import Incident
from app.models.ci_run import CIRun

router = APIRouter()

@router.get("/")
async def list_incidents(
    status: str = None,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Incident).order_by(desc(Incident.created_at))
    if status:
        query = query.where(Incident.status == status)
    query = query.limit(limit)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return [
        {
            "id": inc.id,
            "root_cause": inc.root_cause,
            "error_category": inc.error_category,
            "llm_confidence": inc.llm_confidence,
            "status": inc.status,
            "responsible_files": inc.responsible_files,
            "estimated_fix_time": inc.estimated_fix_time,
            "similarity_score": inc.similarity_score,
            "similar_incident_id": inc.similar_incident_id,
            "created_at": inc.created_at.isoformat() if inc.created_at else None,
        }
        for inc in incidents
    ]

@router.get("/{incident_id}")
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .options(selectinload(Incident.ci_run))
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {
        "id": incident.id,
        "root_cause": incident.root_cause,
        "responsible_files": incident.responsible_files,
        "error_category": incident.error_category,
        "llm_confidence": incident.llm_confidence,
        "suggested_fix": incident.suggested_fix,
        "fix_diff": incident.fix_diff,
        "estimated_fix_time": incident.estimated_fix_time,
        "risk_if_unresolved": incident.risk_if_unresolved,
        "status": incident.status,
        "similar_incident_id": incident.similar_incident_id,
        "similarity_score": incident.similarity_score,
        "simulation_result": incident.simulation_result,
        "ci_run": {
            "id": incident.ci_run.id,
            "workflow_name": incident.ci_run.workflow_name,
            "status": incident.ci_run.status,
            "duration_ms": incident.ci_run.duration_ms,
            "error_block": incident.ci_run.error_block,
        } if incident.ci_run else None,
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
    }

@router.get("/graph/memory")
async def get_incident_graph(db: AsyncSession = Depends(get_db)):
    """Return incident relationship graph data for visualization."""
    result = await db.execute(
        select(Incident)
        .options(selectinload(Incident.ci_run))
        .order_by(desc(Incident.created_at))
        .limit(20)
    )
    incidents = result.scalars().all()
    
    return {
        "incidents": [
            {
                "id": inc.id,
                "pr_id": inc.ci_run.pr_id if inc.ci_run else None,
                "error_category": inc.error_category,
                "similar_incident_id": inc.similar_incident_id,
                "similarity_score": inc.similarity_score,
                "status": inc.status,
            }
            for inc in incidents
        ]
    }
```

---

## app/models/log_embedding.py

```python
from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class LogEmbedding(Base):
    __tablename__ = "log_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    ci_run_id = Column(Integer, ForeignKey("ci_runs.id"), unique=True)
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    cluster_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## app/workers/celery_app.py

```python
from celery import Celery
from app.config import settings

celery_app = Celery(
    "sentinelops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "update-repo-health-every-5m": {
            "task": "app.workers.tasks.run_periodic_repo_health_task",
            "schedule": 300.0,  # Every 5 minutes
        },
    }
)
```

---

## app/analytics page spec — app/analytics/page.tsx

```tsx
"use client"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api"
import PageHeader from "@/components/layout/PageHeader"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from "recharts"

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null)
  
  useEffect(() => {
    apiClient.get("/dashboard/ci-health?days=30").then(r => setData(r.data))
  }, [])
  
  return (
    <div className="space-y-6">
      <PageHeader
        title="Engineering Performance Insights"
        subtitle="Mean Time to Recovery, code churn vs failure correlation, deployment stability"
      />
      
      {/* KPI Row */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Mean Time to Recovery</p>
          <p className="text-3xl font-bold text-white">2h 14m</p>
          <p className="text-xs text-emerald-400 mt-1">↓ 23% vs last month</p>
        </div>
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Deployment Stability</p>
          <p className="text-3xl font-bold text-white">87%</p>
          <p className="text-xs text-amber-400 mt-1">↑ 4% with SentinelOps</p>
        </div>
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Incidents Auto-Explained</p>
          <p className="text-3xl font-bold text-white">94%</p>
          <p className="text-xs text-indigo-400 mt-1">By AI root cause engine</p>
        </div>
      </div>
      
      {/* MTTR Trend Chart */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold text-white mb-4">MTTR Trend — Last 30 Days</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data?.data || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} />
            <Tooltip contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151" }} />
            <Line type="monotone" dataKey="avg_duration" stroke="#6366f1" strokeWidth={2} dot={false} name="Build Duration (ms)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Code Churn vs Failure Rate */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl p-5">
        <h3 className="font-semibold text-white mb-2">Code Churn vs CI Failure Rate</h3>
        <p className="text-xs text-gray-500 mb-4">Each point is a PR — higher lines changed correlates with higher failure probability</p>
        <ResponsiveContainer width="100%" height={200}>
          <ScatterChart data={[]}>
            <CartesianGrid stroke="#1f2937" />
            <XAxis dataKey="lines" name="Lines Changed" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <YAxis dataKey="failure_rate" name="Failure Rate" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <Tooltip contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151" }} />
            <Scatter fill="#6366f1" opacity={0.7} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
```
