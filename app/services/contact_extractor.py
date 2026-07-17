import re
import phonenumbers
from bs4 import BeautifulSoup

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

EMAIL_BLOCKLIST_DOMAINS = {"example.com", "sentry.io", "wixpress.com", "godaddy.com"}

# File extensions that regex mistakes for TLDs (e.g. "logo@2x.png")
FAKE_TLD_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "svg", "webp", "ico",
    "css", "js", "woff", "woff2", "ttf", "eot",
}

DEFAULT_PHONE_REGION = "AE"  # fallback country hint; we'll make this dynamic later


EMAIL_BLOCKLIST_DOMAINS_CONTAINS = ["wixpress.com", "sentry.io", "godaddy.com", "example.com"]

PLACEHOLDER_LOCAL_PARTS = {"youremail", "yourname", "email", "test", "someone", "name"}


def extract_emails(html_text: str) -> list[str]:
    found = set(EMAIL_REGEX.findall(html_text))
    clean = []
    for email in found:
        local_part, domain = email.lower().split("@")[0], email.lower().split("@")[-1]
        tld = domain.split(".")[-1]

        if tld in FAKE_TLD_EXTENSIONS:
            continue
        if any(blocked in domain for blocked in EMAIL_BLOCKLIST_DOMAINS_CONTAINS):
            continue
        if local_part in PLACEHOLDER_LOCAL_PARTS:
            continue

        clean.append(email.lower())
    return clean


def extract_phones(html_text: str, default_region: str = DEFAULT_PHONE_REGION) -> list[str]:
    """
    Extracts phone numbers from tel: links and visible page text only
    (never from raw HTML/JS), validated using the phonenumbers library.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    candidates = set()

    # Source 1: tel: links - most reliable
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href.lower().startswith("tel:"):
            candidates.add(href[4:].strip())

    # Source 2: visible rendered text only, not raw HTML/scripts
    visible_text = soup.get_text(separator=" ")
    for match in phonenumbers.PhoneNumberMatcher(visible_text, default_region):
        candidates.add(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))

    # Validate everything (including tel: links) - drop anything not a real number
    validated = set()
    for raw in candidates:
        try:
            parsed = phonenumbers.parse(raw, default_region)
            if phonenumbers.is_valid_number(parsed):
                validated.add(phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164))
        except phonenumbers.NumberParseException:
            continue

    return list(validated)


def classify_email(email: str) -> str:
    local_part = email.split("@")[0].lower()

    if any(k in local_part for k in ["hr", "career", "job", "recruit"]):
        return "hr"
    if any(k in local_part for k in ["sales", "biz", "business"]):
        return "sales"
    if any(k in local_part for k in ["support", "help", "care"]):
        return "support"
    if any(k in local_part for k in ["info", "contact", "hello", "admin"]):
        return "general"
    return "unclassified"