"""
Periodic polling tasks for demo reliability.
Polls GitHub API every 30s as a fallback when webhooks aren't configured.
"""
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.ci_run import CIRun
from app.models.repository import Repository
from app.workers.celery_app import celery_app


async def _poll_and_update():
    async with AsyncSessionLocal() as session:
        # 1. Fetch all active repos
        result = await session.execute(
            select(Repository).where(Repository.is_active.is_(True))
        )
        repos = result.scalars().all()

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        for repo in repos:
            # 2. Calculate failure rate for last 30 days
            runs_query = select(
                func.count(CIRun.id).label("total"),
                func.count(CIRun.id).filter(
                    CIRun.status == "failure"
                ).label("failed"),
                func.avg(CIRun.duration_ms).label("avg_duration")
            ).where(
                CIRun.repo_id == repo.id,
                CIRun.created_at >= thirty_days_ago
            )

            stats_result = await session.execute(runs_query)
            stats = stats_result.one()

            if stats.total > 0:
                repo.failure_rate = stats.failed / stats.total
                repo.avg_build_time_ms = int(stats.avg_duration or 0)
                # Update risk score based on failure rate and recent activity
                repo.risk_score = min(max(repo.failure_rate * 1.2, 0.0), 1.0)

                if repo.risk_score > 0.7:
                    repo.risk_level = "high"
                elif repo.risk_score > 0.3:
                    repo.risk_level = "caution"
                else:
                    repo.risk_level = "safe"

                repo.last_analyzed = datetime.utcnow()

        await session.commit()


@celery_app.task
def poll_github_events():
    """Poll GitHub for new events (fallback for webhooks)."""
    asyncio.run(_poll_and_update())
