from app.services.apify_service import apify_service
from app.services.crawler_service import crawl_website
from app.services.validation_service import build_final_lead
from app.utils.dedup import is_duplicate, mark_as_seen

leads = apify_service.scrape_google_maps(business_type="dentist", location="Dubai", max_results=3)

for lead in leads:
    print(f"\n=== {lead.business_name} ===")
    crawl_result = crawl_website(lead.website) if lead.website else None
    final = build_final_lead(lead, crawl_result)

    if is_duplicate(final["domain_key"]):
        print(f"  SKIPPED - duplicate of an already-processed domain: {final['domain_key']}")
        continue

    mark_as_seen(final["domain_key"])

    for key, value in final.items():
        print(f"  {key}: {value}")