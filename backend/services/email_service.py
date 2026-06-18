import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_NAME, SMTP_HOST, SMTP_PORT, SMTP_FROM_EMAIL, APP_NAME, APP_URL

logger = logging.getLogger(__name__)


def send_notification(
    to_email: str,
    form_title: str,
    submission_data: dict,
    form_id: int,
    submission_id: int,
) -> bool:
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping email notification")
        return False

    try:
        fields_html = ""
        for key, value in submission_data.items():
            fields_html += f"<tr><td style='padding:8px 12px;border:1px solid #ddd;font-weight:600'>{key}</td><td style='padding:8px 12px;border:1px solid #ddd'>{value}</td></tr>"

        html_body = f"""
        <div style="max-width:600px;margin:0 auto;font-family:Arial,sans-serif">
            <div style="background:#4f46e5;padding:24px;border-radius:12px 12px 0 0">
                <h1 style="color:#fff;margin:0;font-size:22px">&#10003; Submission Received</h1>
            </div>
            <div style="border:1px solid #e5e7eb;border-top:0;padding:24px;border-radius:0 0 12px 12px">
                <p style="font-size:16px;color:#374151">Thank you for submitting the form <strong>"{form_title}"</strong>.</p>
                <p style="font-size:14px;color:#6b7280;margin-bottom:16px">
                    Submission ID: <strong>#{submission_id}</strong>
                </p>
                <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
                    <thead>
                        <tr style="background:#f3f4f6">
                            <th style="padding:8px 12px;border:1px solid #ddd;text-align:left">Field</th>
                            <th style="padding:8px 12px;border:1px solid #ddd;text-align:left">Value</th>
                        </tr>
                    </thead>
                    <tbody>{fields_html}</tbody>
                </table>
                <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0">
                <p style="font-size:12px;color:#9ca3af;text-align:center">
                    {APP_NAME} &mdash; <a href="{APP_URL}" style="color:#4f46e5">{APP_URL}</a>
                </p>
            </div>
        </div>
        """

        message = MIMEMultipart("alternative")
        message["Subject"] = f"Submission Confirmation — {form_title}"
        message["From"] = f"{SMTP_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        if SMTP_PORT == 587:
            server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM_EMAIL, to_email, message.as_string())
        server.quit()

        logger.info("Notification email sent to %s", to_email)
        return True

    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, str(e))
        return False


def send_admin_notification(
    admin_email: str,
    form_title: str,
    submission_data: dict,
    form_id: int,
    submission_id: int,
) -> bool:
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping admin notification")
        return False

    try:
        fields_html = ""
        for key, value in submission_data.items():
            fields_html += f"<tr><td style='padding:8px 12px;border:1px solid #ddd;font-weight:600'>{key}</td><td style='padding:8px 12px;border:1px solid #ddd'>{value}</td></tr>"

        html_body = f"""
        <div style="max-width:600px;margin:0 auto;font-family:Arial,sans-serif">
            <div style="background:#dc2626;padding:24px;border-radius:12px 12px 0 0">
                <h1 style="color:#fff;margin:0;font-size:22px">&#9993; New Form Submission</h1>
            </div>
            <div style="border:1px solid #e5e7eb;border-top:0;padding:24px;border-radius:0 0 12px 12px">
                <p style="font-size:16px;color:#374151">A new submission was received for <strong>"{form_title}"</strong>.</p>
                <p style="font-size:14px;color:#6b7280;margin-bottom:16px">
                    Submission ID: <strong>#{submission_id}</strong>
                </p>
                <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
                    <thead>
                        <tr style="background:#f3f4f6">
                            <th style="padding:8px 12px;border:1px solid #ddd;text-align:left">Field</th>
                            <th style="padding:8px 12px;border:1px solid #ddd;text-align:left">Value</th>
                        </tr>
                    </thead>
                    <tbody>{fields_html}</tbody>
                </table>
                <p style="margin-top:16px">
                    <a href="{APP_URL}/submissions.html?form_id={form_id}"
                       style="display:inline-block;background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-size:14px">
                        View All Submissions
                    </a>
                </p>
                <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0">
                <p style="font-size:12px;color:#9ca3af;text-align:center">
                    {APP_NAME} &mdash; <a href="{APP_URL}" style="color:#4f46e5">{APP_URL}</a>
                </p>
            </div>
        </div>
        """

        message = MIMEMultipart("alternative")
        message["Subject"] = f"New Submission — {form_title}"
        message["From"] = f"{SMTP_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = admin_email
        message.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        if SMTP_PORT == 587:
            server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM_EMAIL, admin_email, message.as_string())
        server.quit()

        logger.info("Admin notification sent to %s", admin_email)
        return True

    except Exception as e:
        logger.error("Failed to send admin email to %s: %s", admin_email, str(e))
        return False
