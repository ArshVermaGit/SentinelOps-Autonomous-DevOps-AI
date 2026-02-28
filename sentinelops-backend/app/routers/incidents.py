"""
Incident Management Router
Author: Arsh Verma
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
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
