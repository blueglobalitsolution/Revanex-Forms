import hashlib
import hmac
import json
import logging
import razorpay
from backend.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

logger = logging.getLogger(__name__)

_client = None


def get_client():
    global _client
    if _client is None and RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        _client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    return _client


def create_order(amount: int, currency: str = "INR") -> dict | None:
    client = get_client()
    if not client:
        logger.warning("Razorpay not configured")
        return None
    try:
        order = client.order.create({
            "amount": amount,
            "currency": currency,
            "payment_capture": 1,
        })
        return order
    except Exception as e:
        logger.error("Failed to create Razorpay order: %s", str(e))
        return None


def verify_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> bool:
    if not RAZORPAY_KEY_SECRET:
        logger.warning("Razorpay secret not configured")
        return False
    try:
        generated = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return generated == razorpay_signature
    except Exception as e:
        logger.error("Payment verification failed: %s", str(e))
        return False


def fetch_payment(payment_id: str) -> dict | None:
    client = get_client()
    if not client:
        return None
    try:
        return client.payment.fetch(payment_id)
    except Exception as e:
        logger.error("Failed to fetch payment %s: %s", payment_id, str(e))
        return None
