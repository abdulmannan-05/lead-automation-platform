from app.workers.email_tasks import send_email_campaign_task

result = send_email_campaign_task.delay(
    subject="Quick note for {business_name}",
    body_template="Hi {business_name} team,\n\nThis is a test message from our outreach system.\n\nBest,\nYour Name",
    delay_seconds_between=5,
)

print(f"Campaign task queued! ID: {result.id}")