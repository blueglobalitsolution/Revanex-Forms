import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/revanex_forms")

SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_NAME = os.getenv("SMTP_NAME", "Revanex Forms")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreplay@reevanax.com")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

APP_NAME = os.getenv("APP_NAME", "Revanex Forms")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "info.reevanax@gmail.com")
