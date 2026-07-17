from app.services.linkedin_service import fetch_linkedin_company_info

test_urls = [
    "https://linkedin.com/company/pearl-dental-clinic-dubai",
    "https://linkedin.com/company/go-dental-clinic-dubai",
]

for url in test_urls:
    print(f"\n=== {url} ===")
    result = fetch_linkedin_company_info(url)
    for k, v in result.items():
        print(f"  {k}: {v}")