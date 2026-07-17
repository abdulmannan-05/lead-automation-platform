import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_email(to_email: str, subject: str, plain_body: str, html_body: str | None = None) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.default_email_sender_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(plain_body, "plain"))
    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, to_email, msg.as_string())