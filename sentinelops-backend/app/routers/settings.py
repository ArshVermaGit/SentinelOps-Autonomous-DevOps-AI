"""
SentinelOps Settings Router
Author: Arsh Verma
"""


from app.core.database import get_db
from app.models.notification import Notification
from app.models.repository import Repository
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Return current platform settings and monitored repositories."""
    repos_result = await db.execute(select(Repository).order_by(Repository.name))
    repos = repos_result.scalars().all()

    return {
        "repositories": [
            {
                "id": r.id,
                "name": r.name,
                "full_name": r.full_name,
                "url": r.url,
                "is_active": r.is_active,
                "risk_score": r.risk_score,
                "failure_rate": r.failure_rate,
                "last_analyzed": r.last_analyzed.isoformat() if r.last_analyzed else None,
            }
            for r in repos
        ],
        "notifications": {
            "email_enabled": False,
            "slack_enabled": False,
            "webhook_url": None,
            "notify_on_high_risk_pr": True,
            "notify_on_ci_failure": True,
            "notify_on_incident": True,
        },
        "ai": {
            "openai_model": "gpt-4o",
            "ml_model_trained": True,
            "embedding_model": "all-MiniLM-L6-v2",
        },
    }


@router.get("/notifications")
async def get_notifications(
    limit: int = 20,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Return recent notifications."""
    from sqlalchemy import desc

    query = select(Notification).order_by(desc(Notification.created_at))
    if status:
        query = query.where(Notification.is_read == status)
    query = query.limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return [
        {
            "id": n.id,
            "type": n.type,
            "severity": n.severity,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "incident_id": n.incident_id,
            "ci_run_id": n.ci_run_id,
            "pr_id": n.pr_id,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ]


class NotificationMarkRead(BaseModel):
    ids: list[int] = []
    mark_all: bool = False


@router.post("/notifications/read")
async def mark_notifications_read(req: NotificationMarkRead, db: AsyncSession = Depends(get_db)):
    """Mark notifications as read."""
    if req.mark_all:
        result = await db.execute(select(Notification).where(Notification.is_read == "unread"))
        for n in result.scalars().all():
            n.is_read = "read"
    else:
        for nid in req.ids:
            result = await db.execute(select(Notification).where(Notification.id == nid))
            n = result.scalar_one_or_none()
            if n:
                n.is_read = "read"

    await db.commit()
    return {"status": "ok"}


@router.put("/repositories/{repo_id}/toggle")
async def toggle_repository(repo_id: int, db: AsyncSession = Depends(get_db)):
    """Toggle repository active monitoring on/off."""
    result = await db.execute(select(Repository).where(Repository.id == repo_id))
    repo = result.scalar_one_or_none()

    if not repo:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Repository not found")

    repo.is_active = not repo.is_active
    await db.commit()

    return {
        "id": repo.id,
        "name": repo.name,
        "is_active": repo.is_active,
    }
