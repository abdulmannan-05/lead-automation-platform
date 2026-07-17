from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "lead_automation",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.scrape_tasks",
        "app.workers.email_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,
    task_soft_time_limit=1700,
    task_routes={
        "app.workers.scrape_tasks.*": {"queue": "scrape"},
        "app.workers.email_tasks.*": {"queue": "email"},
    },
    redbeat_redis_url=settings.redis_url,
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_key_prefix="redbeat:",
)

celery_app.autodiscover_tasks(["app.workers"])