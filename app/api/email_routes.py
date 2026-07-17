from fastapi import APIRouter
from app.schemas.job_schema import EmailCampaignRequest
from app.workers.email_tasks import send_email_campaign_task
from app.services.sheets_service import sheets_service
router = APIRouter(prefix="/email", tags=["email"])


@router.post("/campaign")
def trigger_email_campaign(request: EmailCampaignRequest):
    task = send_email_campaign_task.delay(
        subject=request.subject,
        body_template=request.body_template,
        delay_seconds_between=request.delay_seconds_between,
    )
    return {"task_id": task.id, "status": "queued"}

@router.get("/preview")
def preview_campaign():
    leads = sheets_service.get_leads_ready_for_email()
    return {
        "count": len(leads),
        "recipients": [
            {"business_name": l.get("business_name"), "email": l.get("email_primary")}
            for l in leads
        ],
    }
