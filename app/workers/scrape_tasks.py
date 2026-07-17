from app.workers.celery_app import celery_app
from app.services.pipeline_service import run_scrape_job


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def run_scrape_job_task(self, business_type: str, location: str, max_results: int = 50) -> dict:
    """
    Celery wrapper around our proven synchronous pipeline.
    """
    return run_scrape_job(business_type=business_type, location=location, max_results=max_results)