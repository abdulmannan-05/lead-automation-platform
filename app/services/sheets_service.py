import gspread
from google.oauth2.service_account import Credentials

from app.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

COMPANIES_HEADERS = [
    "lead_id", "business_name", "category", "address", "website",
    "phone_primary", "phones_all", "email_primary", "emails_all",
    "google_rating", "review_count", "google_maps_url", "place_id",
    "search_query", "domain_key", "social_linkedin", "linkedin_type",
    "social_facebook", "social_instagram", "social_twitter", "social_youtube",
    "enrichment_status", "email_status", "date_scraped",
    "linkedin_description", "linkedin_followers", "linkedin_fetch_status",
    "about_context",
]

PEOPLE_HEADERS = ["lead_id", "business_name", "name", "title", "source_url"]


class SheetsService:
    def __init__(self):
        credentials = Credentials.from_service_account_file(
            settings.google_service_account_file, scopes=SCOPES
        )
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open_by_key(settings.google_sheet_id)

    def append_company_row(self, lead: dict) -> None:
        worksheet = self.spreadsheet.worksheet("Companies")
        row = [lead.get(col, "") or "" for col in COMPANIES_HEADERS]
        worksheet.append_row(row, value_input_option="RAW")

    def append_company_rows_batch(self, leads: list[dict]) -> None:
        if not leads:
            return
        worksheet = self.spreadsheet.worksheet("Companies")
        rows = [[lead.get(col, "") or "" for col in COMPANIES_HEADERS] for lead in leads]
        worksheet.append_rows(rows, value_input_option="RAW")

    def append_people_rows_batch(self, lead_id: str, business_name: str, people: list[dict]) -> None:
        if not people:
            return
        worksheet = self.spreadsheet.worksheet("People")
        rows = [[lead_id, business_name, p["name"], p.get("title", ""), p["source_url"]] for p in people]
        worksheet.append_rows(rows, value_input_option="RAW")

    def get_leads_ready_for_email(self) -> list[dict]:
        worksheet = self.spreadsheet.worksheet("Companies")
        records = worksheet.get_all_records()
        ready = []
        for i, record in enumerate(records, start=2):
            if record.get("email_primary") and record.get("email_status") == "not_sent":
                record["_row_number"] = i
                ready.append(record)
        return ready

    def update_email_status(self, row_number: int, status: str, sent_at: str = "") -> None:
        worksheet = self.spreadsheet.worksheet("Companies")
        headers = worksheet.row_values(1)
        status_col = headers.index("email_status") + 1
        worksheet.update_cell(row_number, status_col, status)

    def get_all_companies(self, limit: int = 100) -> list[dict]:
        worksheet = self.spreadsheet.worksheet("Companies")
        records = worksheet.get_all_records()
        return records[-limit:] if len(records) > limit else records

sheets_service = SheetsService()