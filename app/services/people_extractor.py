import re
from bs4 import BeautifulSoup

NAME_PATTERN = re.compile(r'^(Dr\.?\s+)?[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2}$')

# Broadened to cover medical + general professional titles across industries
TITLE_KEYWORDS = [
    "dentist", "surgeon", "orthodontist", "periodontist", "endodontist",
    "hygienist", "physician", "doctor", "consultant", "specialist",
    "therapist", "nurse", "practitioner", "provider", "implantologist",
    "founder", "co-founder", "ceo", "cto", "coo", "director", "manager",
    "hr", "human resources", "head of", "lead", "chief", "president",
    "coordinator", "supervisor", "administrator", "owner", "officer",
]

# Common navigation/section labels that falsely match the name pattern
NAV_BLOCKLIST = {
    "our team", "services", "blog", "gallery", "career", "home", "about",
    "contact", "faq", "faqs", "privacy policy", "our doctors", "team",
    "location", "reviews", "testimonials", "our services",
}


def extract_people_from_page(html_text: str, source_url: str) -> list[dict]:
    """
    Extracts named people from a team/about page. Requires either a "Dr."
    prefix or a nearby recognized professional title to accept a candidate -
    this trades some recall (bare first names with no title context are
    dropped) for real precision against menu/section noise.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    people = []

    candidate_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "strong", "b"])

    for tag in candidate_tags:
        name_text = tag.get_text(strip=True)

        if not name_text or len(name_text) > 60:
            continue
        if name_text.lower() in NAV_BLOCKLIST:
            continue
        if not NAME_PATTERN.match(name_text):
            continue

        is_doctor_prefixed = name_text.lower().startswith("dr.") or name_text.lower().startswith("dr ")

        title_text = ""
        next_el = tag.find_next(["p", "span", "div", "h4", "h5", "h6"])
        if next_el:
            candidate_title = next_el.get_text(strip=True)
            if candidate_title and len(candidate_title) < 100 and not NAME_PATTERN.match(candidate_title):
                if any(keyword in candidate_title.lower() for keyword in TITLE_KEYWORDS):
                    title_text = candidate_title

        # Only accept if we have EITHER a Dr. prefix OR a confirmed title
        if is_doctor_prefixed or title_text:
            people.append({
                "name": name_text,
                "title": title_text,
                "source_url": source_url,
            })

    seen = set()
    unique_people = []
    for p in people:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique_people.append(p)

    return unique_people