"""
services/email_service.py — Resend API integration for sending contact emails.

Sends a nicely formatted HTML email to the portfolio owner whenever
someone submits the contact form.
"""

import logging
import resend

from backend.config import settings

logger = logging.getLogger(__name__)


def send_contact_email(name: str, sender_email: str, message: str, subject: str = "New Contact Form Submission") -> None:
    """Send a contact form submission to the portfolio owner via Resend."""
    resend.api_key = settings.resend_api_key

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <style>
        body {{
          font-family: 'Hanken Grotesk', Arial, sans-serif;
          background: #fcf9f8;
          color: #1c1b1b;
          padding: 40px 24px;
          margin: 0;
        }}
        .card {{
          max-width: 600px;
          margin: 0 auto;
          background: #ffffff;
          border: 1px solid #c3c8c4;
          border-radius: 4px;
          padding: 40px;
        }}
        .label {{
          font-size: 11px;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: #434845;
          margin-bottom: 4px;
        }}
        .value {{
          font-size: 16px;
          color: #1c1b1b;
          margin-bottom: 24px;
          line-height: 1.6;
        }}
        .message-box {{
          background: #f6f3f2;
          border-left: 3px solid #18241f;
          padding: 16px 20px;
          border-radius: 2px;
          font-size: 16px;
          line-height: 1.7;
          color: #1c1b1b;
          white-space: pre-wrap;
        }}
        h1 {{
          font-size: 24px;
          font-weight: 600;
          color: #18241f;
          margin: 0 0 32px;
          border-bottom: 1px solid #c3c8c4;
          padding-bottom: 16px;
        }}
        .footer {{
          margin-top: 32px;
          font-size: 13px;
          color: #737875;
          text-align: center;
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>📬 New Portfolio Contact</h1>

        <p class="label">From</p>
        <p class="value">{name}</p>

        <p class="label">Email</p>
        <p class="value"><a href="mailto:{sender_email}" style="color:#18241f;">{sender_email}</a></p>

        <p class="label">Subject</p>
        <p class="value">{subject}</p>

        <p class="label">Message</p>
        <div class="message-box">{message}</div>

        <div class="footer">
          Sent via your portfolio contact form · debabratadey9090@gmail.com
        </div>
      </div>
    </body>
    </html>
    """

    try:
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": settings.mail_to,
            "reply_to": sender_email,
            "subject": f"[Portfolio] {subject} (from {name})",
            "html": html_body,
        })
        logger.info("Email sent successfully. Resend ID: %s", response.get("id"))
    except Exception as exc:
        logger.error("Failed to send email via Resend: %s", exc)
        raise RuntimeError(f"Email delivery failed: {exc}") from exc
