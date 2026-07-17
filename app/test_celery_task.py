from app.workers.scrape_tasks import run_scrape_job_task

# .delay() kicks it off asynchronously into Redis instantly
result = run_scrape_job_task.delay(business_type="dentist", location="Dubai", max_results=3)

print(f"Task queued! Task ID: {result.id}")
print("Check your Celery worker terminal - it should start processing now.")