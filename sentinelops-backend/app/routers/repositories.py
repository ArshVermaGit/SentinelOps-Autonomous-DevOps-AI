"""
SentinelOps Repository Management Router
Author: Arsh Verma
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.repository import Repository

router = APIRouter()

@router.get("/")
async def list_repositories(db: AsyncSession = Depends(get_db)):
    """List all monitored repositories."""
    result = await db.execute(
        select(Repository).order_by(desc(Repository.risk_score))
    )
    repos = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "full_name": r.full_name,
            "url": r.url,
            "risk_score": r.risk_score,
            "failure_rate": r.failure_rate,
            "deployment_stability": r.deployment_stability,
            "last_analyzed": r.last_analyzed.isoformat() if r.last_analyzed else None,
        }
        for r in repos
    ]
