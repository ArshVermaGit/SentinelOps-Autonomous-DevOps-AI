"""
SentinelOps Dashboard Router
Author: Arsh Verma
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.repository import Repository
from app.models.ci_run import CIRun
from app.models.incident import Incident
from app.models.pull_request import PullRequest
from datetime import datetime, timedelta

from app.services.local_git_service import local_git

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Main dashboard summary — all key metrics."""
    from app.config import settings
    print(f"DEBUG: Dashboard hitting DB -> {settings.DATABASE_URL}")
    
    # Sync real-world local data to DB on every refresh
    await local_git.sync_repositories(db)
    
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
    
    from app.services.resilience_service import resilience_engine
    pulse = await resilience_engine.calculate_pulse(db)
    
    return {
        "pulse": pulse,
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

@router.post("/ai-chat")
async def chat_with_sentinel(payload: dict, db: AsyncSession = Depends(get_db)):
    """AI Chat endpoint for natural language DevOps queries."""
    from app.services.ai_chat_service import handle_devops_query
    from app.services.resilience_service import resilience_engine
    
    # Gather context
    pulse = await resilience_engine.calculate_pulse(db)
    high_risk_prs = await db.execute(select(func.count(PullRequest.id)).where(PullRequest.risk_level == "high"))
    open_incidents = await db.execute(select(func.count(Incident.id)).where(Incident.status == "open"))
    
    context = {
        "pulse": pulse,
        "high_risk_count": high_risk_prs.scalar(),
        "open_incident_count": open_incidents.scalar(),
        "top_risk_repo": "SentinelOps Core" # Placeholder for demo context
    }
    
    response = await handle_devops_query(payload.get("query", ""), context)
    return {"response": response}

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

@router.get("/activities")
async def get_recent_activities(limit: int = 15, db: AsyncSession = Depends(get_db)):
    """Fetch a unified list of recent system activities for the live feed."""
    activities = []
    
    # 1. Recent Incidents
    inc_query = await db.execute(select(Incident).order_by(desc(Incident.created_at)).limit(limit))
    for inc in inc_query.scalars().all():
        activities.append({
            "id": f"inc_{inc.id}",
            "type": "incident",
            "message": f"AI analysis complete: {inc.root_cause[:50]}...",
            "time": inc.created_at,
            "timestamp": inc.created_at,
        })
        
    # 2. Recent CI Runs (Failures and Successes)
    run_query = await db.execute(select(CIRun).order_by(desc(CIRun.started_at)).limit(limit))
    for run in run_query.scalars().all():
        activities.append({
            "id": f"run_{run.id}",
            "type": "success" if run.status == "success" else "failure",
            "message": f"CI {run.status}: {run.workflow_name}",
            "time": run.started_at,
            "timestamp": run.started_at,
        })
        
    # 3. High Risk PRs
    pr_query = await db.execute(
        select(PullRequest)
        .where(PullRequest.risk_level.in_(["high", "caution"]))
        .order_by(desc(PullRequest.created_at))
        .limit(limit)
    )
    for pr in pr_query.scalars().all():
        activities.append({
            "id": f"pr_{pr.id}",
            "type": "pr_risk",
            "message": f"{'🔴 High-risk' if pr.risk_level == 'high' else '🟡 Caution'}: PR '{pr.title}'",
            "time": pr.created_at,
            "timestamp": pr.created_at,
        })
        
    # Sort chronologically (newest first)
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Format times relative for the frontend (simplified relative simulation)
    from datetime import datetime
    now = datetime.utcnow()
    for act in activities:
        diff = now - act["timestamp"]
        mins = int(diff.total_seconds() / 60)
        act["time"] = "just now" if mins == 0 else f"{mins}m ago" if mins < 60 else f"{mins//60}h ago"
        del act["timestamp"] # Clean up sort key
        
    return activities[:limit]
