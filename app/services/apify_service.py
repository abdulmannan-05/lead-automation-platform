from apify_client import ApifyClient
from app.core.config import settings

from app.schemas.lead_schema import RawGoogleMapsLead


def map_apify_item_to_lead(item: dict) -> RawGoogleMapsLead | None:
    """
    Converts one raw Apify dataset item into our clean RawGoogleMapsLead schema.
    Returns None if the item is unusable (e.g., missing a business name).
    """
    business_name = item.get("title")
    if not business_name:
        return None  # skip junk records with no name at all

    location = item.get("location") or {}
    categories = item.get("categories") or []

    return RawGoogleMapsLead(
        business_name=business_name,
        category=item.get("categoryName"),
        all_categories=", ".join(categories) if categories else None,
        address=item.get("address"),
        website=item.get("website"),
        phone=item.get("phoneUnformatted"),
        google_rating=item.get("totalScore"),
        review_count=item.get("reviewsCount"),
        google_maps_url=item.get("url"),
        place_id=item.get("placeId"),
        latitude=location.get("lat"),
        longitude=location.get("lng"),
        search_query=item.get("searchString"),
        country_code=item.get("countryCode"),
    )

class ApifyService:
    """
    Handles all communication with Apify's Google Maps Scraper actor.
    """

    def __init__(self):
        self.client = ApifyClient(settings.apify_token)
        self.actor_id = settings.apify_google_maps_actor_id

    def scrape_google_maps(self, business_type: str, location: str, max_results: int = 50) -> list[RawGoogleMapsLead]:
        run_input = {
            "searchStringsArray": [f"{business_type} in {location}"],
            "maxCrawledPlacesPerSearch": max_results,
            "language": "en",
        }

        run = self.client.actor(self.actor_id).call(run_input=run_input)

        if run is None:
            raise RuntimeError("Apify actor run failed to start")

        dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]

        leads = []
        skipped = 0
        for item in self.client.dataset(dataset_id).iterate_items():
            lead = map_apify_item_to_lead(item)
            if lead is None:
                skipped += 1
                continue
            leads.append(lead)

        print(f"Mapped {len(leads)} leads, skipped {skipped} unusable records")
        return leads


# Single shared instance, since it's stateless besides holding the client
apify_service = ApifyService()