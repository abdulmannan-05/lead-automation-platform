import re
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LeadAutomationBot/1.0; +https://example.com/bot)"
}


def fetch_linkedin_company_info(linkedin_url: str, timeout: int = 10) -> dict:
    """
    Best-effort extraction of publicly available LinkedIn company preview data
    (Open Graph meta tags only - no login, no JS execution).
    Many requests will fail or return partial data - this is expected.
    """
    result = {
        "linkedin_description": None,
        "linkedin_followers": None,
        "fetch_status": "failed",
    }

    if not linkedin_url or "/company/" not in linkedin_url:
        result["fetch_status"] = "skipped_not_company_page"
        return result

    try:
        with httpx.Client(headers=HEADERS, timeout=timeout, follow_redirects=True) as client:
            response = client.get(linkedin_url)
            if response.status_code >= 400:
                result["fetch_status"] = f"blocked_http_{response.status_code}"
                return result
            html_text = response.text
    except httpx.RequestError as e:
        result["fetch_status"] = f"error_{type(e).__name__}"
        return result

    desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html_text)
    if desc_match:
        description = desc_match.group(1)
        result["linkedin_description"] = description

        followers_match = re.search(r'([\d,]+)\s+followers', description, re.IGNORECASE)
        if followers_match:
            result["linkedin_followers"] = followers_match.group(1).replace(",", "")

        result["fetch_status"] = "success"
    else:
        result["fetch_status"] = "no_meta_found"

    return result