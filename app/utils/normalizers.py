from urllib.parse import urljoin, urlparse


def normalize_url(url: str) -> str:
    """
    Cleans a URL so we don't treat 'site.com' and 'site.com/' as different pages.
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    return normalized.lower()


def is_same_domain(base_url: str, candidate_url: str) -> bool:
    """
    Checks if candidate_url belongs to the same domain as base_url.
    Prevents the crawler from wandering off to other websites.
    """
    base_domain = urlparse(base_url).netloc.replace("www.", "")
    candidate_domain = urlparse(candidate_url).netloc.replace("www.", "")
    return base_domain == candidate_domain


def is_valid_scheme(url: str) -> bool:
    """
    Only allow http/https links - blocks things like mailto:, tel:, javascript:, ftp:
    """
    return urlparse(url).scheme in ("http", "https")


def resolve_link(base_url: str, href: str) -> str:
    """
    Converts a relative link (e.g. '/contact') into a full URL
    using the page it was found on as the base.
    """
    return urljoin(base_url, href)

PRIORITY_KEYWORDS = ["contact", "about", "team", "staff", "leadership", "our-team"]


def extract_internal_links(html_text: str, base_url: str) -> list[str]:
    """
    Pulls all <a href="..."> links from HTML, resolves them to full URLs,
    keeps only same-domain http/https links, and sorts priority pages first.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_text, "html.parser")
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        full_url = resolve_link(base_url, href)

        if not is_valid_scheme(full_url):
            continue
        if not is_same_domain(base_url, full_url):
            continue

        links.append(normalize_url(full_url))

    # Deduplicate while preserving some order
    unique_links = list(dict.fromkeys(links))

    # Priority pages first
    priority = [l for l in unique_links if any(k in l for k in PRIORITY_KEYWORDS)]
    rest = [l for l in unique_links if l not in priority]

    return priority + rest