from fastapi import APIRouter
from app.schemas.job_schema import ScrapeJobRequest
from app.workers.scrape_tasks import run_scrape_job_task
from app.services.sheets_service import sheets_service


router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("/")
def trigger_scrape(request: ScrapeJobRequest):
    task = run_scrape_job_task.delay(
        business_type=request.business_type,
        location=request.location,
        max_results=request.max_results,
    )
    return {"task_id": task.id, "status": "queued"}


@router.get("/status/{task_id}")
def get_scrape_status(task_id: str):
    from celery.result import AsyncResult
    from app.workers.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }


@router.get("/leads")
def get_leads(limit: int = 100):
    return {"leads": sheets_service.get_all_companies(limit=limit)}