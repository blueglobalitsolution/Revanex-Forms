import sys
import os
import logging
logging.basicConfig(level=logging.INFO)

sys.path.insert(0, os.getcwd())
from backend.services.email_service import send_notification

result = send_notification(
    to_email="bhavanbadhe@gmail.com",
    form_title="Test Form",
    submission_data={"Name": "Test User"},
    form_id=1,
    submission_id=1234
)

print(f"Email sent successfully: {result}")
