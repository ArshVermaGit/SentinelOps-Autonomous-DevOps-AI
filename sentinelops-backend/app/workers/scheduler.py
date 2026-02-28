"""
Periodic polling tasks for demo reliability.
Polls GitHub API every 30s as a fallback when webhooks aren't configured.
"""
from app.workers.celery_app import celery_app


@celery_app.task
def poll_github_events():
    """Poll GitHub for new events (fallback for webhooks)."""
    # Placeholder: In production, this would poll the GitHub Events API
    pass
