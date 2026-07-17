from app.services.sheets_service import sheets_service

test_lead = {
    "lead_id": "test-001",
    "business_name": "Test Business",
    "category": "Testing",
    "address": "123 Test Street",
    "website": "https://example.com",
    "phone_primary": "+971500000000",
    "phones_all": "+971500000000",
    "email_primary": "test@example.com",
    "emails_all": "test@example.com",
    "google_rating": 4.5,
    "review_count": 10,
    "google_maps_url": "https://maps.google.com/test",
    "place_id": "test-place-id",
    "search_query": "test in Testland",
    "domain_key": "example.com",
    "social_linkedin": "https://linkedin.com/company/test",
    "linkedin_type": "company",
    "social_facebook": None,
    "social_instagram": None,
    "social_twitter": None,
    "social_youtube": None,
    "enrichment_status": "success",
    "email_status": "not_sent",
    "date_scraped": "2026-07-10",
}

sheets_service.append_company_row(test_lead)
print("Row written successfully - check your Google Sheet!")