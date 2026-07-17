from app.services.scheduler_service import schedule_recurring_scrape, list_scheduled_jobs

schedule_recurring_scrape(
    job_name="dubai_clinics_daily",
    business_type="clinic",
    location="Dubai",
    max_results=10,
    cron={"hour": "*", "minute": "*/2"},  # TEST ONLY: every 2 minutes
)

print("Scheduled! Current jobs:")
print(list_scheduled_jobs())