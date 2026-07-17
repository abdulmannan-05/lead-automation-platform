from app.services.people_extractor import extract_people_from_page
import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeadAutomationBot/1.0)"}
with httpx.Client(headers=HEADERS, timeout=10, follow_redirects=True) as client:
    html = client.get("https://pearldentalclinics.com/our-team").text

people = extract_people_from_page(html, "https://pearldentalclinics.com/our-team")
for p in people:
    print(p)