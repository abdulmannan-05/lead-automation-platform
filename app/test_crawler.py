import httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeadAutomationBot/1.0)"}
url = "http://islamabaddentist.net"

with httpx.Client(headers=HEADERS, timeout=10, follow_redirects=True) as client:
    response = client.get(url)
    print("Final URL after redirects:", response.url)
    print("Status:", response.status_code)
    html_text = response.text

soup = BeautifulSoup(html_text, "html.parser")

meta_desc = soup.find("meta", attrs={"name": "description"})
print("Meta description tag found:", meta_desc)

visible_text = soup.get_text(separator=" ", strip=True)
print("Visible text length:", len(visible_text))
print("First 300 chars of visible text:", visible_text[:300])