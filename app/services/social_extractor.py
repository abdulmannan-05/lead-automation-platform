import re

SOCIAL_PATTERNS = {
    "linkedin": re.compile(r"linkedin\.com/[^\s\"'<>]+", re.IGNORECASE),
    "facebook": re.compile(r"facebook\.com/[^\s\"'<>]+", re.IGNORECASE),
    "instagram": re.compile(r"instagram\.com/[^\s\"'<>]+", re.IGNORECASE),
    "twitter": re.compile(r"(?:twitter|x)\.com/[^\s\"'<>]+", re.IGNORECASE),
    "youtube": re.compile(r"youtube\.com/[^\s\"'<>]+", re.IGNORECASE),
}

# Signals that a matched link is a "share this page" button, not a real profile
JUNK_LINK_MARKERS = ["share?", "sharer", "intent/tweet", "TWITTER_HANDLE", "FACEBOOK_HANDLE"]


def extract_social_links(html_text: str) -> dict[str, str]:
    results = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        for match in pattern.finditer(html_text):
            url = match.group(0).rstrip("/\"'")

            if any(marker in url for marker in JUNK_LINK_MARKERS):
                continue  # skip share buttons, keep looking

            if not url.startswith("http"):
                url = "https://" + url

            results[platform] = url
            break  # take the first VALID match for this platform, then stop

    return results


def get_linkedin_page_type(linkedin_url: str) -> str:
    """
    Distinguishes a LinkedIn company page from a personal profile link.
    """
    if "/company/" in linkedin_url:
        return "company"
    if "/in/" in linkedin_url:
        return "personal"
    return "unknown"