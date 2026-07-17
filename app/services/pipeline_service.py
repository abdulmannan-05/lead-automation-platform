import uuid
from datetime import date

from app.services.apify_service import apify_service
from app.services.crawler_service import crawl_website
from app.services.validation_service import build_final_lead
from app.services.sheets_service import sheets_service
from app.utils.dedup import is_duplicate, mark_as_seen


def run_scrape_job(business_type: str, location: str, max_results: int = 50) -> dict:
    """
    Full pipeline: Apify scrape -> crawl each website -> validate -> dedup -> write to Sheets.
    Returns a summary dict of what happened, for logging/status purposes.
    """
    summary = {
        "business_type": business_type,
        "location": location,
        "total_scraped": 0,
        "duplicates_skipped": 0,
        "written_to_sheet": 0,
        "crawl_failed": 0,
        "no_website": 0,
        "errors": [],
    }

    try:
        maps_leads = apify_service.scrape_google_maps(
            business_type=business_type, location=location, max_results=max_results
        )
    except Exception as e:
        summary["errors"].append(f"Apify scrape failed entirely: {e}")
        return summary

    summary["total_scraped"] = len(maps_leads)
    today = date.today().isoformat()
    leads_to_write = []

    for maps_lead in maps_leads:
        try:
            crawl_result = None
            if maps_lead.website:
                crawl_result = crawl_website(maps_lead.website)

            final_lead = build_final_lead(maps_lead, crawl_result)

            if is_duplicate(final_lead["domain_key"]):
                summary["duplicates_skipped"] += 1
                continue

            mark_as_seen(final_lead["domain_key"])

            final_lead["lead_id"] = str(uuid.uuid4())
            final_lead["date_scraped"] = today

            # Pull people out BEFORE appending to Companies — it's not a Company column
            people = final_lead.pop("people", [])
            if people:
                try:
                    sheets_service.append_people_rows_batch(
                        final_lead["lead_id"], final_lead["business_name"], people
                    )
                except Exception as e:
                    summary["errors"].append(
                        f"Failed writing people for '{final_lead['business_name']}': {e}"
                    )

            if final_lead["enrichment_status"] == "no_website":
                summary["no_website"] += 1
            elif final_lead["enrichment_status"] == "failed":
                summary["crawl_failed"] += 1

            leads_to_write.append(final_lead)

        except Exception as e:
            # One bad lead should never kill the whole batch
            summary["errors"].append(f"Failed processing '{maps_lead.business_name}': {e}")
            continue


    try:
        sheets_service.append_company_rows_batch(leads_to_write)
        summary["written_to_sheet"] = len(leads_to_write)
    except Exception as e:
        summary["errors"].append(f"Failed writing to Sheets: {e}")

    return summary