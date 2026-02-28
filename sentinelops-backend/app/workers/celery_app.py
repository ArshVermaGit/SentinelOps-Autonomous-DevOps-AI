from celery import Celery
from app.config import settings

celery_app = Celery(
    "sentinelops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "update-repo-health-every-5m": {
            "task": "app.workers.tasks.run_periodic_repo_health_task",
            "schedule": 300.0,  # Every 5 minutes
        },
    }
)
