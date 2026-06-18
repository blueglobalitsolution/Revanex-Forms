import logging
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Form, Submission
from backend.schemas import (
    PaymentOrderRequest,
    PaymentOrderResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from backend.services.payment_service import create_order, verify_payment
from backend.config import RAZORPAY_KEY_ID

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/forms", tags=["payments"])


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def get_form_by_id_or_slug(db: Session, form_id_or_slug: str) -> Form:
    try:
        form_id = int(form_id_or_slug)
        form = db.query(Form).filter(Form.id == form_id).first()
        if form:
            return form
    except ValueError:
        pass
    
    target_slug = slugify(form_id_or_slug)
    form = db.query(Form).filter(Form.slug == target_slug).first()
    if form:
        return form

    return db.query(Form).filter(func.lower(Form.title) == form_id_or_slug.lower()).first()


@router.post("/{form_id}/payment/order", response_model=PaymentOrderResponse)
def create_payment_order(
    form_id: str,
    payload: PaymentOrderRequest,
    db: Session = Depends(get_db),
):
    form = get_form_by_id_or_slug(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if not form.razorpay_enabled:
        raise HTTPException(status_code=400, detail="Payments are not enabled for this form")

    if payload.amount < 100:
        raise HTTPException(status_code=400, detail="Minimum amount is 100 paise (₹1)")

    order = create_order(amount=payload.amount, currency=payload.currency)
    if not order:
        raise HTTPException(status_code=500, detail="Failed to create payment order")

    return PaymentOrderResponse(
        order_id=order["id"],
        amount=order["amount"],
        currency=order["currency"],
        key_id=RAZORPAY_KEY_ID,
    )


@router.post("/{form_id}/payment/verify", response_model=PaymentVerifyResponse)
def verify_payment_signature(
    form_id: str,
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
):
    form = get_form_by_id_or_slug(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    is_valid = verify_payment(
        razorpay_order_id=payload.razorpay_order_id,
        razorpay_payment_id=payload.razorpay_payment_id,
        razorpay_signature=payload.razorpay_signature,
    )

    if is_valid:
        if payload.submission_id:
            submission = db.query(Submission).filter(
                Submission.id == payload.submission_id
            ).first()
            if submission:
                submission.payment_id = payload.razorpay_payment_id
                submission.payment_status = "captured"
                db.commit()
                
                # Send emails on successful payment
                from backend.services.email_service import send_notification, send_admin_notification
                from backend.config import ADMIN_EMAIL
                try:
                    if submission.respondent_email:
                        send_notification(
                            to_email=submission.respondent_email,
                            form_title=form.title,
                            submission_data=submission.data,
                            form_id=form.id,
                            submission_id=submission.id,
                        )
                    
                    send_admin_notification(
                        admin_email=ADMIN_EMAIL,
                        form_title=form.title,
                        submission_data=submission.data,
                        form_id=form.id,
                        submission_id=submission.id,
                    )
                except Exception as e:
                    logger.error("Email notification error after payment: %s", str(e))

        return PaymentVerifyResponse(
            status="success",
            message="Payment verified successfully",
        )
    else:
        return PaymentVerifyResponse(
            status="failed",
            message="Payment verification failed",
        )
