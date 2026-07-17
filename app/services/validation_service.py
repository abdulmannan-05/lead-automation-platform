import phonenumbers
from urllib.parse import urlparse

from app.schemas.lead_schema import RawGoogleMapsLead
from app.services.social_extractor import get_linkedin_page_type
from app.services.linkedin_service import fetch_linkedin_company_info


def normalize_phone(raw_phone: str | None, region: str = "AE") -> str | None:
    """
    Validates and formats a phone number to E.164. Returns None if invalid/missing.
    """
    if not raw_phone:
        return None
    try:
        parsed = phonenumbers.parse(raw_phone, region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    return None


def get_domain_key(website: str | None) -> str | None:
    """
    Produces a normalized domain string for dedup purposes.
    e.g. 'https://www.example.com/page' -> 'example.com'
    """
    if not website:
        return None
    domain = urlparse(website).netloc.lower()
    return domain.replace("www.", "") or None


def build_final_lead(maps_lead: RawGoogleMapsLead, crawl_result: dict | None) -> dict:
    """
    Combines the Apify lead and crawl result into one final, clean record
    ready to be written to Google Sheets.
    """
    region = maps_lead.country_code.upper() if maps_lead.country_code else "AE"

    maps_phone_clean = normalize_phone(maps_lead.phone, region=region)

    if crawl_result is None:
        enrichment_status = "no_website"
        emails, phones, socials, about_context, people = [], [], {}, None, []
    else:
        enrichment_status = crawl_result["crawl_status"]
        emails = crawl_result["emails"]
        phones = crawl_result["phones"]
        socials = crawl_result["social_links"]
        about_context = crawl_result.get("about_context")
        people = crawl_result.get("people", [])

    all_phones = list(dict.fromkeys(filter(None, [maps_phone_clean] + phones)))
    email_primary = emails[0] if emails else None

    linkedin_url = socials.get("linkedin")
    linkedin_type = get_linkedin_page_type(linkedin_url) if linkedin_url else None

    linkedin_info = {"linkedin_description": None, "linkedin_followers": None, "fetch_status": "not_attempted"}
    if linkedin_type == "company":
        linkedin_info = fetch_linkedin_company_info(linkedin_url)

    return {
        "business_name": maps_lead.business_name,
        "category": maps_lead.category,
        "address": maps_lead.address,
        "website": maps_lead.website,
        "google_rating": maps_lead.google_rating,
        "review_count": maps_lead.review_count,
        "google_maps_url": maps_lead.google_maps_url,
        "place_id": maps_lead.place_id,
        "search_query": maps_lead.search_query,

        "domain_key": get_domain_key(maps_lead.website),
        "phone_primary": all_phones[0] if all_phones else None,
        "phones_all": ", ".join(all_phones),
        "email_primary": email_primary,
        "emails_all": ", ".join(emails),

        "social_linkedin": linkedin_url,
        "linkedin_type": linkedin_type,
        "social_facebook": socials.get("facebook"),
        "social_instagram": socials.get("instagram"),
        "social_twitter": socials.get("twitter"),
        "social_youtube": socials.get("youtube"),

        "linkedin_description": linkedin_info["linkedin_description"],
        "linkedin_followers": linkedin_info["linkedin_followers"],
        "linkedin_fetch_status": linkedin_info["fetch_status"],

        "enrichment_status": enrichment_status,
        "email_status": "not_sent",
        "about_context": about_context,
        "people": people,
    }