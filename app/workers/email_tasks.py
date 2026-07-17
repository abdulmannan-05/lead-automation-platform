from datetime import datetime
from app.workers.celery_app import celery_app
from app.services.sheets_service import sheets_service
from app.services.email_service import send_email
from app.services.email_templates import render_default_email
from app.core.config import settings


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def send_single_email_task(self, row_number: int, to_email: str, subject: str, plain_body: str, html_body: str = None):
    try:
        send_email(to_email, subject, plain_body, html_body)
        sheets_service.update_email_status(row_number, "sent", datetime.utcnow().isoformat())
        return {"row": row_number, "status": "sent"}
    except Exception as e:
        sheets_service.update_email_status(row_number, "failed")
        raise


@celery_app.task
def send_email_campaign_task(subject: str = None, body_template: str = None, delay_seconds_between: int = 10):
    leads = sheets_service.get_leads_ready_for_email()

    for i, lead in enumerate(leads):
        business_name = lead.get("business_name", "")

        if subject and body_template:
            final_subject = subject.format(business_name=business_name)
            final_plain = body_template.format(business_name=business_name)
            final_html = None  # manual override stays plain-text only, kept simple
        else:
            final_subject, final_plain, final_html = render_default_email(
                business_name=business_name,
                category=lead.get("category", ""),
                location=lead.get("search_query", "").replace(lead.get("category", ""), "").strip(),
                sender_name=settings.default_email_sender_name,
                sender_email=settings.smtp_from_email,
            )

        send_single_email_task.apply_async(
            args=[lead["_row_number"], lead["email_primary"], final_subject, final_plain, final_html],
            countdown=i * delay_seconds_between,
        )

    return {"queued": len(leads)}