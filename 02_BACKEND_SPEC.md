# SentinelOps — Backend Specification

## Project Structure

```
sentinelops-backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings from env vars
│   ├── database.py                # SQLAlchemy async setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── repository.py          # Repository ORM model
│   │   ├── pull_request.py        # PullRequest ORM model
│   │   ├── ci_run.py              # CIRun ORM model
│   │   ├── incident.py            # Incident ORM model
│   │   └── log_embedding.py       # LogEmbedding ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── repository.py          # Pydantic schemas
│   │   ├── pull_request.py
│   │   ├── ci_run.py
│   │   ├── incident.py
│   │   └── dashboard.py           # Aggregated dashboard schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── webhooks.py            # GitHub webhook receiver
│   │   ├── repositories.py        # Repo management endpoints
│   │   ├── pull_requests.py       # PR analysis endpoints
│   │   ├── incidents.py           # Incident endpoints
│   │   ├── dashboard.py           # Dashboard aggregation endpoints
│   │   ├── analysis.py            # Manual trigger analysis
│   │   └── simulation.py          # Self-healing simulation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github_service.py      # GitHub API client
│   │   ├── risk_analyzer.py       # Static risk analysis
│   │   ├── ci_analyzer.py         # CI pattern analysis
│   │   ├── ml_predictor.py        # ML model inference
│   │   ├── llm_service.py         # OpenAI integration
│   │   ├── embedding_service.py   # SentenceTransformers
│   │   ├── similarity_service.py  # Log similarity search
│   │   └── websocket_service.py   # WebSocket broadcast
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py          # Celery configuration
│   │   ├── tasks.py               # All Celery tasks
│   │   └── scheduler.py           # Periodic polling tasks
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── train.py               # Model training script
│   │   ├── model.pkl              # Trained model (generated)
│   │   └── synthetic_data.py      # Generate training data
│   └── utils/
│       ├── __init__.py
│       ├── log_parser.py          # Log text parsing utilities
│       ├── diff_parser.py         # Git diff parsing
│       └── mock_data.py           # Demo mock data generator
├── alembic/                       # Database migrations
│   ├── env.py
│   └── versions/
├── tests/
│   ├── test_risk_analyzer.py
│   ├── test_ci_analyzer.py
│   ├── test_llm_service.py
│   └── test_webhooks.py
├── scripts/
│   └── seed_demo_data.py          # Seed DB with realistic demo data
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import create_tables
from app.routers import webhooks, repositories, pull_requests, incidents, dashboard, analysis, simulation
from app.workers.celery_app import celery_app
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    title="SentinelOps API",
    description="Autonomous DevOps AI Co-Pilot — Engineering Decision Intelligence",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["Repositories"])
app.include_router(pull_requests.router, prefix="/api/pull-requests", tags=["Pull Requests"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])

@app.get("/health")
async def health():
    return {"status": "operational", "service": "SentinelOps"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## app/config.py

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/sentinelops"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    
    # GitHub
    GITHUB_TOKEN: str
    GITHUB_WEBHOOK_SECRET: str = "sentinelops_secret"
    
    # App
    SECRET_KEY: str = "sentinelops_dev_key"
    DEBUG: bool = True
    
    # ML Model
    MODEL_PATH: str = "app/ml/model.pkl"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## app/database.py

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## app/models/repository.py

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)  # "owner/repo"
    url = Column(String, nullable=False)
    
    # Risk metrics
    risk_score = Column(Float, default=0.0)        # 0.0 - 1.0
    failure_rate = Column(Float, default=0.0)      # Historical failure rate
    avg_build_time_ms = Column(Integer, default=0)
    deployment_stability = Column(Float, default=1.0)  # 0.0 - 1.0
    
    # Tracking
    last_analyzed = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pull_requests = relationship("PullRequest", back_populates="repository")
    ci_runs = relationship("CIRun", back_populates="repository")
```

---

## app/models/pull_request.py

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    github_pr_number = Column(Integer, nullable=False)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    
    # PR metadata
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    base_branch = Column(String, default="main")
    head_branch = Column(String, nullable=False)
    
    # Risk analysis inputs
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    file_types = Column(JSON, default=list)           # [".py", ".js", ...]
    has_config_changes = Column(Boolean, default=False)
    has_test_changes = Column(Boolean, default=False)
    has_dependency_changes = Column(Boolean, default=False)
    
    # Risk analysis outputs
    risk_probability = Column(Float, default=0.0)    # 0.0 - 1.0
    risk_level = Column(String, default="unknown")   # "safe" | "caution" | "high"
    risk_factors = Column(JSON, default=list)         # List of contributing factors
    
    # Status
    status = Column(String, default="open")          # "open" | "merged" | "closed"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    ci_runs = relationship("CIRun", back_populates="pull_request")
```

---

## app/models/ci_run.py

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class CIRun(Base):
    __tablename__ = "ci_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    github_run_id = Column(Integer, unique=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=True)
    
    # Run metadata
    workflow_name = Column(String, nullable=False)
    status = Column(String, nullable=False)          # "success" | "failure" | "running" | "cancelled"
    conclusion = Column(String, nullable=True)
    
    # Timing
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    duration_ms = Column(Integer, default=0)
    is_anomalous_duration = Column(Boolean, default=False)
    
    # Log analysis
    log_text = Column(Text, nullable=True)           # Raw log (truncated to last 200 lines)
    error_block = Column(Text, nullable=True)        # Extracted error section
    failure_step = Column(String, nullable=True)     # Which step failed
    
    # Pattern analysis
    cluster_id = Column(Integer, nullable=True)      # Log embedding cluster
    is_flaky = Column(Boolean, default=False)
    anomaly_flags = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="ci_runs")
    pull_request = relationship("PullRequest", back_populates="ci_runs")
    incident = relationship("Incident", back_populates="ci_run", uselist=False)
```

---

## app/models/incident.py

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    ci_run_id = Column(Integer, ForeignKey("ci_runs.id"), unique=True)
    
    # LLM Root Cause Analysis
    root_cause = Column(Text, nullable=True)
    responsible_files = Column(JSON, default=list)
    error_category = Column(String, nullable=True)   # "dependency|syntax|test|config|runtime|network"
    llm_confidence = Column(Float, default=0.0)
    
    # Fix suggestion
    suggested_fix = Column(Text, nullable=True)
    fix_diff = Column(Text, nullable=True)           # Unified diff format
    estimated_fix_time = Column(String, nullable=True)
    risk_if_unresolved = Column(Text, nullable=True)
    
    # Similarity
    similar_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    similarity_score = Column(Float, default=0.0)    # 0.0 - 1.0
    
    # Resolution
    status = Column(String, default="open")          # "open" | "simulated" | "resolved"
    simulation_result = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ci_run = relationship("CIRun", back_populates="incident")
```

---

## app/services/risk_analyzer.py

```python
from typing import Dict, List, Any
import re

class RiskAnalyzer:
    """Static risk analysis for pull requests."""
    
    # Risk weights (sum to 1.0)
    WEIGHTS = {
        "lines_changed": 0.25,
        "file_type_risk": 0.20,
        "author_history": 0.25,
        "dependency_changes": 0.20,
        "pr_size_ratio": 0.10,
    }
    
    HIGH_RISK_FILE_TYPES = {".json", ".yaml", ".yml", ".toml", ".env", ".tf", ".dockerfile"}
    LOW_RISK_FILE_TYPES = {".md", ".txt", ".rst"}
    
    def analyze_pr(self, pr_data: Dict[str, Any], author_history: Dict) -> Dict:
        """
        Returns risk assessment for a pull request.
        
        pr_data: {
            lines_added, lines_deleted, files_changed,
            file_types: [str], has_config_changes, has_dependency_changes,
            has_test_changes
        }
        author_history: {
            total_prs, failed_prs, avg_lines_changed
        }
        """
        
        # 1. Lines changed score
        total_lines = pr_data.get("lines_added", 0) + pr_data.get("lines_deleted", 0)
        lines_score = min(total_lines / 1000, 1.0)  # Normalize to 1000 lines = max risk
        
        # 2. File type risk
        file_types = set(pr_data.get("file_types", []))
        high_risk_overlap = file_types & self.HIGH_RISK_FILE_TYPES
        low_risk_overlap = file_types & self.LOW_RISK_FILE_TYPES
        file_type_score = (
            len(high_risk_overlap) * 0.3 +
            (0.2 if pr_data.get("has_config_changes") else 0) +
            (0.2 if pr_data.get("has_dependency_changes") else 0) +
            (-0.1 if pr_data.get("has_test_changes") else 0)  # Tests reduce risk
        )
        file_type_score = max(0.0, min(1.0, file_type_score))
        
        # 3. Author history score
        total = author_history.get("total_prs", 0)
        failed = author_history.get("failed_prs", 0)
        author_score = (failed / total) if total > 0 else 0.3  # Unknown author = 30% baseline
        
        # 4. Dependency changes
        dependency_score = 1.0 if pr_data.get("has_dependency_changes") else 0.0
        
        # 5. PR size ratio (vs author's average)
        avg_lines = author_history.get("avg_lines_changed", 200)
        size_ratio = total_lines / max(avg_lines, 1)
        pr_size_score = min(size_ratio / 5, 1.0)  # 5x average = max risk
        
        # Weighted sum
        risk_probability = (
            self.WEIGHTS["lines_changed"] * lines_score +
            self.WEIGHTS["file_type_risk"] * file_type_score +
            self.WEIGHTS["author_history"] * author_score +
            self.WEIGHTS["dependency_changes"] * dependency_score +
            self.WEIGHTS["pr_size_ratio"] * pr_size_score
        )
        
        risk_probability = round(min(max(risk_probability, 0.0), 1.0), 3)
        
        # Risk level classification
        if risk_probability < 0.35:
            risk_level = "safe"
        elif risk_probability < 0.65:
            risk_level = "caution"
        else:
            risk_level = "high"
        
        # Risk factors (human readable)
        risk_factors = []
        if lines_score > 0.5:
            risk_factors.append(f"Large change: {total_lines} lines modified")
        if high_risk_overlap:
            risk_factors.append(f"High-risk file types: {', '.join(high_risk_overlap)}")
        if pr_data.get("has_dependency_changes"):
            risk_factors.append("Dependency file changes detected")
        if author_score > 0.4:
            risk_factors.append(f"Author has {int(author_score * 100)}% historical failure rate")
        if size_ratio > 3:
            risk_factors.append(f"PR is {size_ratio:.1f}x larger than author's average")
        
        return {
            "risk_probability": risk_probability,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "component_scores": {
                "lines": lines_score,
                "file_types": file_type_score,
                "author_history": author_score,
                "dependencies": dependency_score,
                "size_ratio": pr_size_score,
            }
        }
```

---

## app/services/llm_service.py

```python
from openai import AsyncOpenAI
from app.config import settings
import json
import re

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

LLM_SYSTEM_PROMPT = """You are SentinelOps, an expert DevOps root cause analyzer. 
You analyze CI/CD failures and provide structured, actionable insights.
Always respond with valid JSON only. No markdown, no preamble."""

LLM_USER_TEMPLATE = """A CI pipeline has failed. Analyze and respond in JSON only.

## Failed CI Log (last 50 lines):
{error_log}

## Code Diff (files changed in this PR):
{code_diff}

## Similar Past Incidents:
{similar_incidents}

## Required JSON Response:
{{
  "root_cause": "string - what caused this failure",
  "responsible_files": ["file1.py"],
  "error_category": "dependency|syntax|test|config|runtime|network",
  "confidence": 0.0,
  "suggested_fix": "string - specific actionable fix",
  "fix_diff": "string - unified diff format patch",
  "risk_if_unresolved": "string - consequences",
  "estimated_fix_time": "5 minutes|1 hour|half day|full day"
}}"""

async def analyze_failure(error_log: str, code_diff: str, similar_incidents: list) -> dict:
    """Call OpenAI to analyze CI failure and return structured root cause."""
    
    similar_text = "\n".join([
        f"- Incident #{inc['id']}: {inc['root_cause']} (similarity: {inc['similarity_score']:.0%})"
        for inc in similar_incidents[:3]
    ]) or "No similar incidents found."
    
    user_message = LLM_USER_TEMPLATE.format(
        error_log=error_log[-3000:],      # Last 3000 chars of log
        code_diff=code_diff[:2000],        # First 2000 chars of diff
        similar_incidents=similar_text
    )
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,  # Low temperature for deterministic analysis
        max_tokens=1500,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    return json.loads(content)


async def analyze_failure_mock(error_log: str) -> dict:
    """Mock LLM response for demo without API key."""
    return {
        "root_cause": "Import error in database connection module caused by missing environment variable DB_HOST",
        "responsible_files": ["app/database.py", "docker-compose.yml"],
        "error_category": "config",
        "confidence": 0.92,
        "suggested_fix": "Add DB_HOST to your environment variables or .env file",
        "fix_diff": "--- a/docker-compose.yml\n+++ b/docker-compose.yml\n@@ -10,6 +10,7 @@\n     environment:\n       - DB_NAME=myapp\n       - DB_USER=postgres\n+      - DB_HOST=postgres\n       - DB_PASSWORD=secret",
        "risk_if_unresolved": "All database operations will fail in CI and production",
        "estimated_fix_time": "5 minutes"
    }
```

---

## app/services/embedding_service.py

```python
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import numpy as np
from app.models.log_embedding import LogEmbedding

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_log(log_text: str) -> list[float]:
    """Create embedding vector for log text."""
    # Clean and truncate log
    clean_log = log_text[-2000:]  # Use last 2000 chars (most relevant)
    embedding = model.encode(clean_log, convert_to_numpy=True)
    return embedding.tolist()

def cosine_similarity(a: list, b: list) -> float:
    """Calculate cosine similarity between two embedding vectors."""
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

async def find_similar_incidents(
    db: AsyncSession,
    log_text: str,
    threshold: float = 0.7,
    limit: int = 3
) -> list[dict]:
    """Find similar past incidents using embedding similarity."""
    
    new_embedding = embed_log(log_text)
    
    # Fetch all stored embeddings
    result = await db.execute(select(LogEmbedding))
    stored = result.scalars().all()
    
    # Calculate similarities
    similarities = []
    for stored_emb in stored:
        sim = cosine_similarity(new_embedding, stored_emb.embedding_vector)
        if sim >= threshold:
            similarities.append({
                "embedding_id": stored_emb.id,
                "ci_run_id": stored_emb.ci_run_id,
                "similarity_score": sim
            })
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similarities[:limit]
```

---

## app/workers/tasks.py

```python
from app.workers.celery_app import celery_app
from app.services.risk_analyzer import RiskAnalyzer
from app.services.llm_service import analyze_failure
from app.services.embedding_service import embed_log, find_similar_incidents
from app.services.github_service import GitHubService
import asyncio

@celery_app.task(bind=True, max_retries=3)
def analyze_pull_request_task(self, pr_id: int, repo_full_name: str):
    """Analyze a PR for risk when it's opened or updated."""
    try:
        asyncio.run(_analyze_pr(pr_id, repo_full_name))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)

@celery_app.task(bind=True, max_retries=3)
def analyze_ci_run_task(self, run_id: int, repo_full_name: str):
    """Analyze completed CI run — trigger LLM if failure."""
    try:
        asyncio.run(_analyze_ci_run(run_id, repo_full_name))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)

@celery_app.task
def run_periodic_repo_health_task():
    """Run every 5 minutes to update repo health metrics."""
    asyncio.run(_update_all_repo_health())

async def _analyze_ci_run(run_id: int, repo_full_name: str):
    from app.database import AsyncSessionLocal
    from app.models.ci_run import CIRun
    from app.models.incident import Incident
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        # Fetch CI run
        result = await db.execute(select(CIRun).where(CIRun.github_run_id == run_id))
        ci_run = result.scalar_one_or_none()
        
        if not ci_run or ci_run.status != "failure":
            return
        
        # Fetch log from GitHub
        gh = GitHubService()
        log_text = await gh.get_run_logs(repo_full_name, run_id)
        ci_run.log_text = log_text
        ci_run.error_block = extract_error_block(log_text)
        
        # Find similar incidents
        similar = await find_similar_incidents(db, log_text)
        
        # LLM analysis
        diff = await gh.get_pr_diff(repo_full_name, ci_run.pr_id) if ci_run.pr_id else ""
        analysis = await analyze_failure(ci_run.error_block, diff, similar)
        
        # Store incident
        incident = Incident(
            ci_run_id=ci_run.id,
            root_cause=analysis["root_cause"],
            responsible_files=analysis["responsible_files"],
            error_category=analysis["error_category"],
            llm_confidence=analysis["confidence"],
            suggested_fix=analysis["suggested_fix"],
            fix_diff=analysis["fix_diff"],
            estimated_fix_time=analysis["estimated_fix_time"],
            risk_if_unresolved=analysis["risk_if_unresolved"],
        )
        db.add(incident)
        
        # Store embedding
        from app.models.log_embedding import LogEmbedding
        embedding = LogEmbedding(
            ci_run_id=ci_run.id,
            embedding_vector=embed_log(log_text)
        )
        db.add(embedding)
        
        await db.commit()
        
        # Broadcast to dashboard via WebSocket
        from app.services.websocket_service import broadcast_new_incident
        await broadcast_new_incident(incident.id)

def extract_error_block(log_text: str, lines: int = 50) -> str:
    """Extract the most relevant error section from log."""
    log_lines = log_text.split("\n")
    
    # Find the last line containing "error" or "Error" or "FAIL"
    error_indices = [
        i for i, line in enumerate(log_lines)
        if any(kw in line for kw in ["Error", "error", "FAIL", "failed", "Exception", "Traceback"])
    ]
    
    if error_indices:
        last_error = error_indices[-1]
        start = max(0, last_error - 20)
        end = min(len(log_lines), last_error + 30)
        return "\n".join(log_lines[start:end])
    
    # Fallback: last N lines
    return "\n".join(log_lines[-lines:])
```

---

## app/routers/webhooks.py

```python
from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
from app.config import settings
from app.workers.tasks import analyze_pull_request_task, analyze_ci_run_task

router = APIRouter()

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    expected = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    payload = await request.body()
    
    # Verify signature (skip in dev mode)
    if not settings.DEBUG:
        if not verify_github_signature(payload, x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    repo_full_name = data.get("repository", {}).get("full_name", "")
    
    if x_github_event == "pull_request":
        action = data.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            pr_number = data["pull_request"]["number"]
            analyze_pull_request_task.delay(pr_number, repo_full_name)
    
    elif x_github_event == "workflow_run":
        action = data.get("action")
        if action == "completed":
            run_id = data["workflow_run"]["id"]
            analyze_ci_run_task.delay(run_id, repo_full_name)
    
    return {"status": "accepted"}
```

---

## app/routers/dashboard.py

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.repository import Repository
from app.models.ci_run import CIRun
from app.models.incident import Incident
from app.models.pull_request import PullRequest
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Main dashboard summary — all key metrics."""
    
    # Repository count and avg risk
    repos_result = await db.execute(select(Repository))
    repos = repos_result.scalars().all()
    
    # CI runs last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    runs_result = await db.execute(
        select(CIRun).where(CIRun.started_at >= thirty_days_ago)
    )
    runs = runs_result.scalars().all()
    
    # Incidents last 30 days
    incidents_result = await db.execute(
        select(Incident).order_by(desc(Incident.created_at)).limit(10)
    )
    recent_incidents = incidents_result.scalars().all()
    
    total_runs = len(runs)
    failed_runs = sum(1 for r in runs if r.status == "failure")
    success_rate = ((total_runs - failed_runs) / total_runs * 100) if total_runs > 0 else 100
    
    # MTTR calculation
    resolved_incidents = [i for i in recent_incidents if i.status == "resolved"]
    
    return {
        "repos": {
            "total": len(repos),
            "high_risk": sum(1 for r in repos if r.risk_score > 0.65),
            "avg_risk_score": sum(r.risk_score for r in repos) / max(len(repos), 1)
        },
        "ci": {
            "total_runs_30d": total_runs,
            "failed_runs_30d": failed_runs,
            "success_rate": round(success_rate, 1),
            "avg_build_time_ms": sum(r.duration_ms for r in runs) // max(len(runs), 1)
        },
        "incidents": {
            "open": sum(1 for i in recent_incidents if i.status == "open"),
            "total_30d": len(recent_incidents),
        },
        "repos_list": [
            {
                "id": r.id,
                "name": r.name,
                "risk_score": r.risk_score,
                "failure_rate": r.failure_rate,
            }
            for r in sorted(repos, key=lambda x: x.risk_score, reverse=True)
        ]
    }

@router.get("/ci-health")
async def get_ci_health(days: int = 30, db: AsyncSession = Depends(get_db)):
    """CI health trends for charting."""
    start = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(CIRun).where(CIRun.started_at >= start).order_by(CIRun.started_at)
    )
    runs = result.scalars().all()
    
    # Group by day
    daily_data = {}
    for run in runs:
        day = run.started_at.strftime("%Y-%m-%d")
        if day not in daily_data:
            daily_data[day] = {"date": day, "success": 0, "failure": 0, "total": 0, "avg_duration": 0}
        daily_data[day]["total"] += 1
        if run.status == "failure":
            daily_data[day]["failure"] += 1
        else:
            daily_data[day]["success"] += 1
        daily_data[day]["avg_duration"] += run.duration_ms
    
    for day in daily_data.values():
        if day["total"] > 0:
            day["avg_duration"] = day["avg_duration"] // day["total"]
    
    return {"data": list(daily_data.values())}

@router.get("/risk-heatmap")
async def get_risk_heatmap(db: AsyncSession = Depends(get_db)):
    """Risk heatmap data — repos and PRs ranked by risk."""
    repos_result = await db.execute(
        select(Repository).order_by(desc(Repository.risk_score))
    )
    repos = repos_result.scalars().all()
    
    prs_result = await db.execute(
        select(PullRequest)
        .where(PullRequest.status == "open")
        .order_by(desc(PullRequest.risk_probability))
        .limit(20)
    )
    prs = prs_result.scalars().all()
    
    return {
        "repositories": [
            {"id": r.id, "name": r.name, "risk_score": r.risk_score, "risk_level": 
             "high" if r.risk_score > 0.65 else "caution" if r.risk_score > 0.35 else "safe"}
            for r in repos
        ],
        "pull_requests": [
            {
                "id": pr.id,
                "title": pr.title,
                "author": pr.author,
                "risk_probability": pr.risk_probability,
                "risk_level": pr.risk_level,
                "risk_factors": pr.risk_factors,
            }
            for pr in prs
        ]
    }
```

---

## app/routers/simulation.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.incident import Incident
from sqlalchemy import select
import asyncio
import random

router = APIRouter()

@router.post("/{incident_id}/apply-fix")
async def simulate_fix(incident_id: int, db: AsyncSession = Depends(get_db)):
    """
    Simulate applying the AI-suggested fix.
    Runs a mock test suite and returns predicted outcome.
    """
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if not incident.suggested_fix:
        raise HTTPException(status_code=400, detail="No fix available for this incident")
    
    # Simulate processing time (makes demo feel real)
    await asyncio.sleep(2)
    
    # Simulation result based on LLM confidence
    success_probability = incident.llm_confidence if incident.llm_confidence else 0.75
    success = random.random() < success_probability
    
    simulation_result = {
        "success": success,
        "steps": [
            {"step": "Apply patch", "status": "success", "duration_ms": 234},
            {"step": "Install dependencies", "status": "success", "duration_ms": 4521},
            {"step": "Run unit tests", "status": "success" if success else "failure", "duration_ms": 12043},
            {"step": "Run integration tests", "status": "success" if success else "skipped", "duration_ms": 8932 if success else 0},
            {"step": "Build Docker image", "status": "success" if success else "skipped", "duration_ms": 23100 if success else 0},
        ],
        "predicted_outcome": "CI pipeline would PASS" if success else "CI pipeline would still FAIL — additional fix required",
        "confidence": f"{int(success_probability * 100)}%",
        "tests_passed": 47 if success else 31,
        "tests_failed": 0 if success else 16,
    }
    
    # Update incident status
    incident.status = "simulated"
    incident.simulation_result = simulation_result
    await db.commit()
    
    return simulation_result
```

---

## requirements.txt

```
fastapi==0.110.0
uvicorn[standard]==0.27.1
sqlalchemy[asyncio]==2.0.28
asyncpg==0.29.0
alembic==1.13.1
pydantic-settings==2.2.1
redis==5.0.1
celery==5.3.6
openai==1.14.3
sentence-transformers==2.5.1
scikit-learn==1.4.1.post1
numpy==1.26.4
httpx==0.27.0
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
websockets==12.0
pytest==8.1.0
pytest-asyncio==0.23.5
```

---

## docker-compose.yml

```yaml
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/sentinelops
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - DEBUG=true
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build: .
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/sentinelops
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    depends_on:
      - postgres
      - redis
    command: celery -A app.workers.celery_app worker --loglevel=info

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sentinelops
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## .env.example

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/sentinelops
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-your-key-here
GITHUB_TOKEN=ghp_your-token-here
GITHUB_WEBHOOK_SECRET=your-webhook-secret
DEBUG=true
```
