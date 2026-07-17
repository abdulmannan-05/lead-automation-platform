from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.scheduler_service import (
    schedule_recurring_scrape,
    schedule_recurring_email_campaign,
    remove_scheduled_job,
    list_scheduled_jobs,
)

router = APIRouter(prefix="/schedules", tags=["schedules"])


class ScheduleScrapeRequest(BaseModel):
    job_name: str = Field(..., min_length=2, max_length=50)
    business_type: str
    location: str
    max_results: int = Field(default=50, ge=1, le=500)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    day_of_week: str = Field(default="*")  # e.g. "mon", "mon,wed,fri", "*" for every day


class ScheduleEmailRequest(BaseModel):
    job_name: str = Field(..., min_length=2, max_length=50)
    subject: str
    body_template: str
    delay_seconds_between: int = Field(default=10, ge=1, le=300)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    day_of_week: str = Field(default="*")


@router.post("/scrape")
def create_scrape_schedule(request: ScheduleScrapeRequest):
    schedule_recurring_scrape(
        job_name=request.job_name,
        business_type=request.business_type,
        location=request.location,
        max_results=request.max_results,
        cron={"hour": request.hour, "minute": request.minute, "day_of_week": request.day_of_week},
    )
    return {"status": "scheduled", "job_name": request.job_name}


@router.post("/email")
def create_email_schedule(request: ScheduleEmailRequest):
    schedule_recurring_email_campaign(
        job_name=request.job_name,
        subject=request.subject,
        body_template=request.body_template,
        delay_seconds_between=request.delay_seconds_between,
        cron={"hour": request.hour, "minute": request.minute, "day_of_week": request.day_of_week},
    )
    return {"status": "scheduled", "job_name": request.job_name}


@router.get("/")
def get_schedules():
    return {"schedules": list_scheduled_jobs()}


@router.delete("/{job_type}/{job_name}")
def delete_schedule(job_type: str, job_name: str):
    if job_type not in ("scrape", "email"):
        raise HTTPException(status_code=400, detail="job_type must be 'scrape' or 'email'")
    remove_scheduled_job(job_name, job_type=job_type)
    return {"status": "deleted", "job_name": job_name}