from app.services.scheduler_service import remove_scheduled_job

remove_scheduled_job("dubai_clinics_daily", job_type="scrape")
print("Test schedule removed.")