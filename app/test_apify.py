from app.services.apify_service import apify_service

results = apify_service.scrape_google_maps(
    business_type="dentist",
    location="Dubai",
    max_results=5,
)

print(f"\nGot {len(results)} clean leads\n")

for lead in results:
    print(lead.model_dump())
    print("---")