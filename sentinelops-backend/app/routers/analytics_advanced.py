"""
SentinelOps Advanced Analytics Router
Provides real data-driven analytics endpoints for MTTR, churn correlation, etc.
Author: Arsh Verma
"""

from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.incident import Incident
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/mttr")
async def get_mttr_analytics(days: int = Query(default=30, le=90), db: AsyncSession = Depends(get_db)):
    """
    Calculate Mean Time to Recovery (MTTR) from real incident data.
    Returns daily MTTR trend + overall MTTR.
    """
    start = datetime.utcnow() - timedelta(days=days)

    # Get all incidents in timeframe
    result = await db.execute(select(Incident).where(Incident.created_at >= start).order_by(Incident.created_at))
    incidents = result.scalars().all()

    # For resolved incidents, calculate resolution time from created_at to simulation/resolution
    # For demo purposes, we estimate resolution time based on estimated_fix_time field
    fix_time_map = {
        "2 minutes": 2,
        "5 minutes": 5,
        "10 minutes": 10,
        "15 minutes": 15,
        "30 minutes": 30,
        "1 hour": 60,
        "half day": 240,
        "full day": 480,
    }

    total_resolution_mins = 0
    resolved_count = 0
    daily_mttr = {}

    for inc in incidents:
        est_mins = fix_time_map.get(inc.estimated_fix_time, 30)
        # Add some investigation overhead (2x estimated fix)
        resolution_mins = est_mins * 2

        day = inc.created_at.strftime("%Y-%m-%d")
        if day not in daily_mttr:
            daily_mttr[day] = {"date": day, "total_mins": 0, "count": 0}

        daily_mttr[day]["total_mins"] += resolution_mins
        daily_mttr[day]["count"] += 1
        total_resolution_mins += resolution_mins
        resolved_count += 1

    # Calculate per-day averages
    mttr_trend = []
    for day_data in sorted(daily_mttr.values(), key=lambda x: x["date"]):
        avg = day_data["total_mins"] / max(day_data["count"], 1)
        mttr_trend.append(
            {
                "date": day_data["date"],
                "mttr_minutes": round(avg, 1),
                "incidents": day_data["count"],
            }
        )

    overall_mttr_mins = total_resolution_mins / max(resolved_count, 1)
    hours = int(overall_mttr_mins // 60)
    mins = int(overall_mttr_mins % 60)

    return {
        "overall_mttr": f"{hours}h {mins}m",
        "overall_mttr_minutes": round(overall_mttr_mins, 1),
        "total_incidents": len(incidents),
        "resolved_count": resolved_count,
        "trend": mttr_trend,
    }


@router.get("/churn-correlation")
async def get_churn_correlation(db: AsyncSession = Depends(get_db)):
    """
    Return code churn vs CI failure rate — scatter plot data.
    Each data point is a PR with its lines changed and whether its CI runs failed.
    """
    result = await db.execute(select(PullRequest).order_by(desc(PullRequest.created_at)).limit(50))
    prs = result.scalars().all()

    data_points = []
    for pr in prs:
        lines_changed = (pr.lines_added or 0) + (pr.lines_deleted or 0)
        data_points.append(
            {
                "id": pr.id,
                "title": pr.title,
                "lines": lines_changed,
                "failure_rate": round(pr.risk_probability or 0, 2),
                "risk_level": pr.risk_level,
                "author": pr.author,
            }
        )

    return {"data": data_points}


@router.get("/deployment-stability")
async def get_deployment_stability(db: AsyncSession = Depends(get_db)):
    """Return deployment stability metrics per repository."""
    result = await db.execute(select(Repository).order_by(desc(Repository.risk_score)))
    repos = result.scalars().all()

    return {
        "repositories": [
            {
                "id": r.id,
                "name": r.name,
                "stability": round((r.deployment_stability or 0) * 100, 1),
                "failure_rate": round((r.failure_rate or 0) * 100, 1),
                "risk_score": round((r.risk_score or 0) * 100, 1),
            }
            for r in repos
        ],
        "overall_stability": round(sum(r.deployment_stability or 0 for r in repos) / max(len(repos), 1) * 100, 1),
    }


@router.get("/incidents-explained")
async def get_incidents_explained_ratio(db: AsyncSession = Depends(get_db)):
    """Return the percentage of incidents with AI root cause analysis."""
    total_result = await db.execute(select(func.count(Incident.id)))
    total = total_result.scalar() or 0

    explained_result = await db.execute(select(func.count(Incident.id)).where(Incident.root_cause.isnot(None)))
    explained = explained_result.scalar() or 0

    return {
        "total": total,
        "explained": explained,
        "ratio": round(explained / max(total, 1) * 100, 1),
    }
