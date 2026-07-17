from redbeat import RedBeatSchedulerEntry
from celery.schedules import crontab
from app.workers.celery_app import celery_app


def schedule_recurring_scrape(job_name: str, business_type: str, location: str, max_results: int, cron: dict) -> None:
    """
    Schedules a recurring scrape job.
    cron example: {"hour": 9, "minute": 0, "day_of_week": "mon"} -> every Monday at 9am
    """
    entry = RedBeatSchedulerEntry(
        name=f"scrape:{job_name}",
        task="app.workers.scrape_tasks.run_scrape_job_task",
        schedule=crontab(**cron),
        args=[business_type, location, max_results],
        app=celery_app,
    )
    entry.save()


def schedule_recurring_email_campaign(job_name: str, subject: str, body_template: str, delay_seconds_between: int, cron: dict) -> None:
    entry = RedBeatSchedulerEntry(
        name=f"email:{job_name}",
        task="app.workers.email_tasks.send_email_campaign_task",
        schedule=crontab(**cron),
        args=[subject, body_template, delay_seconds_between],
        app=celery_app,
    )
    entry.save()


def remove_scheduled_job(job_name: str, job_type: str = "scrape") -> None:
    """
    job_type is 'scrape' or 'email' - must match the prefix used when scheduling.
    """
    entry = RedBeatSchedulerEntry.from_key(f"redbeat:{job_type}:{job_name}", app=celery_app)
    entry.delete()


def list_scheduled_jobs() -> list[str]:
    import redis
    from app.core.config import settings

    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    keys = r.zrange("redbeat::schedule", 0, -1)
    return keys