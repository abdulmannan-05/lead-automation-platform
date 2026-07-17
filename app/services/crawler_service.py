import httpx
from collections import deque
from app.services.people_extractor import extract_people_from_page
from app.core.config import settings
from app.utils.normalizers import normalize_url, extract_internal_links
from app.services.contact_extractor import extract_emails, extract_phones, classify_email
from app.services.social_extractor import extract_social_links
import time

MAX_RETRIES = 1
REQUEST_DELAY_SECONDS = 0.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LeadAutomationBot/1.0; +https://example.com/bot)"
}

PRIORITY_KEYWORDS = ["contact", "about", "team", "staff", "leadership", "our-team"]


def extract_page_context(html_text: str, is_homepage: bool = False) -> str:
    from bs4 import BeautifulSoup
    import unicodedata

    soup = BeautifulSoup(html_text, "html.parser")

    def clean(text: str) -> str:
        # Strip invisible/formatting Unicode chars (e.g. word joiners, zero-width spaces)
        return "".join(ch for ch in text if unicodedata.category(ch)[0] != "C").strip()

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        return clean(meta_desc["content"])[:500]

    if is_homepage:
        visible_text = soup.get_text(separator=" ", strip=True)
        return clean(" ".join(visible_text.split()))[:500]

    return ""

def crawl_website(start_url: str) -> dict:
    """
    Crawls a business website starting from start_url, following internal links
    up to settings.crawler_max_pages, collecting emails, phones, social links,
    named people, and a short company description.
    """
    max_pages = settings.crawler_max_pages
    timeout = settings.crawler_timeout_seconds

    visited = set()
    queue = deque([normalize_url(start_url)])

    all_emails = set()
    all_phones = set()
    all_socials = {}
    all_people = []
    pages_crawled = 0
    had_any_success = False
    errors = []
    about_context = ""

    with httpx.Client(headers=HEADERS, timeout=timeout, follow_redirects=True) as client:
        while queue and len(visited) < max_pages:
            url = queue.popleft()

            if url in visited:
                continue

            is_first_page = (pages_crawled == 0)
            visited.add(url)

            response = None
            last_error = None
            for attempt in range(MAX_RETRIES + 1):
                try:
                    response = client.get(url)
                    if response.status_code >= 400:
                        last_error = f"HTTP {response.status_code}"
                        response = None
                        continue
                    break
                except httpx.TimeoutException:
                    last_error = "timeout"
                except httpx.RequestError as e:
                    last_error = f"{type(e).__name__}: {e}"
                time.sleep(REQUEST_DELAY_SECONDS)

            if response is None:
                errors.append(f"{url} -> {last_error}")
                continue

            time.sleep(REQUEST_DELAY_SECONDS)

            had_any_success = True
            pages_crawled += 1
            html_text = response.text

            if is_first_page and not about_context:
                about_context = extract_page_context(html_text, is_homepage=True)

            all_emails.update(extract_emails(html_text))
            all_phones.update(extract_phones(html_text))

            socials = extract_social_links(html_text)
            for platform, link in socials.items():
                if platform not in all_socials:
                    all_socials[platform] = link

            if any(keyword in url for keyword in PRIORITY_KEYWORDS):
                all_people.extend(extract_people_from_page(html_text, url))

            new_links = extract_internal_links(html_text, url)
            for link in new_links:
                if link not in visited:
                    queue.append(link)

    emails_classified: dict[str, list[str]] = {}
    for email in all_emails:
        category = classify_email(email)
        emails_classified.setdefault(category, []).append(email)

    if not had_any_success:
        status = "failed"
    elif pages_crawled < max_pages and not queue:
        status = "success"
    else:
        status = "partial"

    return {
        "emails": list(all_emails),
        "emails_classified": emails_classified,
        "phones": list(all_phones),
        "social_links": all_socials,
        "pages_crawled": pages_crawled,
        "crawl_status": status,
        "errors": errors,
        "about_context": about_context,
        "people": all_people,
    }