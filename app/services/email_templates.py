DEFAULT_SUBJECT = "Helping {business_name} grow with more customers"

DEFAULT_BODY_PLAIN = """Hi {business_name} team,

I came across {business_name} while researching {category} businesses in {location}, and wanted to reach out directly.

We help businesses like yours attract more customers through improved online visibility and targeted outreach. If that's something you're currently thinking about, I'd love to share a few ideas that might be useful for you.

Would you be open to a quick conversation this week?

Best regards,
{sender_name}

---
If you'd rather not receive future emails like this, just reply and let us know."""

DEFAULT_BODY_HTML = """
<div style="font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; max-width: 560px; margin: 0 auto; color: #1a1a1a; line-height: 1.6;">
  <p>Hi {business_name} team,</p>

  <p>I came across <strong>{business_name}</strong> while researching {category} businesses in {location}, and wanted to reach out directly.</p>

  <p>We help businesses like yours attract more customers through improved online visibility and targeted outreach. If that's something you're currently thinking about, I'd love to share a few ideas that might be useful for you.</p>

  <p>Would you be open to a quick conversation this week?</p>

  <table cellpadding="0" cellspacing="0" style="margin: 20px 0;">
    <tr>
      <td style="background-color: #4f8cff; border-radius: 6px;">
        <a href="mailto:{sender_email}" style="display: inline-block; padding: 10px 20px; color: #ffffff; text-decoration: none; font-weight: 500;">Reply to Chat</a>
      </td>
    </tr>
  </table>

  <p>Best regards,<br>{sender_name}</p>

  <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 24px 0 12px;">
  <p style="font-size: 12px; color: #888;">If you'd rather not receive future emails like this, just reply and let us know.</p>
</div>
"""


def render_default_email(business_name: str, category: str, location: str, sender_name: str, sender_email: str) -> tuple[str, str, str]:
    safe_category = category or "local"
    safe_location = location or "your area"

    subject = DEFAULT_SUBJECT.format(business_name=business_name)
    plain = DEFAULT_BODY_PLAIN.format(
        business_name=business_name, category=safe_category, location=safe_location, sender_name=sender_name,
    )
    html = DEFAULT_BODY_HTML.format(
        business_name=business_name, category=safe_category, location=safe_location,
        sender_name=sender_name, sender_email=sender_email,
    )
    return subject, plain, html