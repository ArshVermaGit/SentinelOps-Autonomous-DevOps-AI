"""
Incident Management Router
Author: Arsh Verma
"""

from app.core.database import get_db
from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.models.pull_request import PullRequest
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/")
async def list_incidents(
    status: str | None = None,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
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


@router.get("/{incident_id}")
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .options(selectinload(Incident.ci_run))
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Build relationship_data for IncidentMemoryGraph
    relationship_data = None
    if incident.ci_run and incident.ci_run.pr_id:
        pr_result = await db.execute(
            select(PullRequest).where(PullRequest.id == incident.ci_run.pr_id)
        )
        pr = pr_result.scalar_one_or_none()
        if pr:
            relationship_data = {
                "pr_id": str(pr.id),
                "pr_title": pr.title,
                "author": pr.author,
                "author_failure_rate": 0.18,  # Could be fetched from GitHub API
                "commits": [{"sha": f"{pr.head_branch[:7]}abc", "message": pr.title}],
                "files": incident.responsible_files or [],
                "ci_run_id": str(incident.ci_run.id),
                "ci_status": incident.ci_run.status,
                "incident_title": (incident.root_cause or "")[:60],
            }

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
        "relationship_data": relationship_data,
        "ci_run": (
            {
                "id": incident.ci_run.id,
                "workflow_name": incident.ci_run.workflow_name,
                "status": incident.ci_run.status,
                "duration_ms": incident.ci_run.duration_ms,
                "error_block": incident.ci_run.error_block,
            }
            if incident.ci_run
            else None
        ),
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
    }


class ResolveRequest(BaseModel):
    resolution_notes: str = ""


@router.patch("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: int, req: ResolveRequest, db: AsyncSession = Depends(get_db)
):
    """Mark an incident as resolved with optional notes."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "resolved"

    # Add timeline event
    event = IncidentEvent(
        incident_id=incident.id,
        event_type="resolved",
        title="Incident resolved",
        description=req.resolution_notes or "Marked as resolved by user.",
        actor="user",
    )
    db.add(event)
    await db.commit()

    return {"status": "resolved", "id": incident.id}


@router.get("/{incident_id}/timeline")
async def get_incident_timeline(incident_id: int, db: AsyncSession = Depends(get_db)):
    """Return chronological event timeline for an incident."""
    result = await db.execute(
        select(IncidentEvent)
        .where(IncidentEvent.incident_id == incident_id)
        .order_by(IncidentEvent.created_at)
    )
    events = result.scalars().all()

    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "title": e.title,
            "description": e.description,
            "actor": e.actor,
            "event_data": e.event_data,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]
