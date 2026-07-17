from app.services.pipeline_service import run_scrape_job

result = run_scrape_job(business_type="dentist", location="Dubai", max_results=5)

print("\n=== JOB SUMMARY ===")
for key, value in result.items():
    print(f"{key}: {value}")