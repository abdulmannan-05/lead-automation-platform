from app.services.scheduler_service import schedule_recurring_scrape

schedule_recurring_scrape(
    job_name="dubai_clinics_weekly",
    business_type="clinic",
    location="Dubai",
    max_results=50,
    cron={"hour": 9, "minute": 0, "day_of_week": "mon"},
)

print("Weekly schedule registered.")