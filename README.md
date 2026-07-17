# Sparkle & Co. — Property Cleaning Lead Management System

A backend service that captures leads from a property cleaning company's contact form, logs them to Google Sheets, notifies both customer and staff by email, and provides an interactive two-way WhatsApp experience for status updates — built with **FastAPI**, **Google Sheets API**, **Gmail SMTP**, and **Twilio (WhatsApp Business API)**.

---

## ✨ Features

- 📝 **Contact form intake** — validated name, email, phone, and project details
- 📊 **Google Sheets integration** — every lead is logged as a durable, human-readable record
- 📧 **Automated email notifications** — a branded acknowledgement to the customer and an internal alert to the company
- 💬 **WhatsApp acknowledgement** — customers are notified the moment their request is received
- 🤖 **Two-way WhatsApp bot** — customers can message back anytime to check their request status, with a professional interactive menu (list picker) for common actions
- 🔒 **Input validation** — strict, whitelist-based validation on names, emails, phone numbers, and project details
- 🌍 **International-ready phone handling** — normalizes any phone format (`0335...`, `92335...`, `+92335...`) into one canonical form used consistently across Sheets, email, and WhatsApp
- 🛡️ **Resilient by design** — a failure in any one integration (Sheets, email, or WhatsApp) never blocks the others or fails the customer's submission

---

## 🏗️ Architecture

```
landing.html (contact form)
       │
       ▼
FastAPI backend
       │
       ├──► Google Sheets   (durable lead record)
       ├──► Gmail SMTP      (customer + company emails)
       └──► Twilio WhatsApp (acknowledgement + 2-way bot)
                  │
                  ▼
        Customer replies on WhatsApp
                  │
                  ▼
        POST /whatsapp/webhook
                  │
                  ▼
        Looks up lead in Google Sheets → replies with live status
```

The API always responds to the customer as soon as their lead is validated and safely recorded — downstream integrations (email, WhatsApp) run independently and are logged on failure rather than blocking the response.

---

## 📁 Project Structure

```
cleaning-lead-api/
├── .env                     # environment variables (not committed)
├── requirements.txt
├── service_account.json     # Google service account credentials (not committed)
├── landing.html             # standalone contact form frontend
└── app/
    ├── main.py               # FastAPI app, routes, WhatsApp webhook & bot logic
    ├── config.py             # centralized settings loaded from .env
    ├── schemas.py             # Pydantic models + validation + phone normalization
    ├── sheets_service.py       # Google Sheets read/write integration
    ├── email_service.py        # branded HTML email sending via Gmail SMTP
    ├── twilio_service.py        # WhatsApp messaging via Twilio
    └── lead_service.py          # orchestrates the full lead workflow
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| Validation | [Pydantic](https://docs.pydantic.dev/) |
| Data Store | Google Sheets ([gspread](https://docs.gspread.org/)) |
| Email | Gmail SMTP (Python `smtplib`) |
| Messaging | [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp) |
| Tunneling (dev) | [ngrok](https://ngrok.com/) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A Google Cloud project with the Sheets API enabled + a Service Account
- A Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) generated
- A [Twilio](https://www.twilio.com/try-twilio) account with the WhatsApp Sandbox activated
- [ngrok](https://ngrok.com/download) for local WhatsApp webhook testing

### Installation

```bash
git clone https://github.com/<your-username>/cleaning-lead-api.git
cd cleaning-lead-api
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# Google Sheets
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SHEET_TAB_NAME=Leads

# Gmail SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_FROM_ADDRESS=your_email@gmail.com
EMAIL_FROM_NAME=Sparkle & Co.
COMPANY_NOTIFICATION_EMAIL=your_email@gmail.com

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_MAIN_MENU_CONTENT_SID=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Place your downloaded Google service-account key as `service_account.json` in the project root, and share your target Google Sheet with the service account's email address (found inside that JSON file).

Your Google Sheet's first row should contain these headers:

| Timestamp | Name | Email | Phone | Project Details | Status |
|---|---|---|---|---|---|

### Running the server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs are auto-generated at `http://127.0.0.1:8000/docs`.

### Testing the WhatsApp bot locally

WhatsApp requires a public URL to deliver incoming messages, so expose your local server with ngrok:

```bash
ngrok http 8000
```

Copy the generated `https://xxxx.ngrok-free.app` URL and set it as your webhook in **Twilio Console → Messaging → Try it out → Sandbox settings → "When a message comes in"**, appending the path:

```
https://xxxx.ngrok-free.app/whatsapp/webhook
```

### Using the contact form

Open `landing.html` directly in your browser — it submits to the FastAPI backend running at `127.0.0.1:8000`.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/leads` | Submits a new lead — validates input, logs to Sheets, sends emails and WhatsApp acknowledgement |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `POST` | `/whatsapp/webhook` | Receives inbound WhatsApp messages from Twilio and routes replies |

### Example request — `POST /leads`

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+923001234567",
  "project_details": "3-bedroom apartment, move-out clean, needed by end of month"
}
```

### Example response

```json
{
  "status": "success",
  "message": "Thanks! We've received your request and will be in touch shortly."
}
```

---

## 💬 WhatsApp Bot Capabilities

Customers can message the business's WhatsApp number at any time:

| Customer says | Bot responds with |
|---|---|
| `menu` / a greeting | An interactive list of options (check status, book a cleaning, get a quote, contact us, and more) |
| `status` / `update` / `progress` | Their live request status, pulled directly from Google Sheets |
| `help` | A list of available commands |
| Anything else | A friendly fallback pointing them to `menu` or `status` |

Status updates reflect the Google Sheet in real time — changing a lead's `Status` cell is immediately reflected the next time the customer checks.

---

## 🛡️ Security Notes

- All user input is validated and sanitized before storage or display (HTML-escaped in emails, formula-escaped in Sheets)
- Secrets (API keys, credentials) are never hardcoded — all configuration is loaded from environment variables
- CORS is currently open (`allow_origins=["*"]`) for local development — **restrict this to your production frontend domain before deploying publicly**
- The WhatsApp integration currently runs on Twilio's sandbox for development; production use requires onboarding to the [WhatsApp Business API](https://www.twilio.com/docs/whatsapp/api) with a dedicated, Meta-verified business number

## ⚠️ Known Limitations

- No rate limiting or bot/spam protection on the public `/leads` endpoint yet
- No duplicate-submission detection
- Twilio webhook does not yet verify that incoming requests genuinely originate from Twilio (signature validation)
- Phone number normalization currently assumes a single default country code

---

## 📄 License

This project is provided as-is for educational and internal business use.

---

## 🙋 Support

For issues or questions, please open an issue in this repository.
