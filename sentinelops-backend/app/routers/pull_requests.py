"""
SentinelOps Pull Request Analysis Router
Author: Arsh Verma
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
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
