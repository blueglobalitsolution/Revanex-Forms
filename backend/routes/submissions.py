import logging
import re
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Form, Submission, User
from backend.routes.auth import get_current_user
from backend.schemas import SubmissionCreate, SubmissionResponse, MessageResponse
from backend.services.email_service import send_notification, send_admin_notification

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/forms", tags=["submissions"])


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


@router.post("/{form_id}/submit", response_model=SubmissionResponse, status_code=201)
def submit_form(
    form_id: str,
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
):
    form = get_form_by_id_or_slug(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if not form.is_active:
        raise HTTPException(status_code=400, detail="This form is no longer accepting submissions")

    submission = Submission(
        form_id=form.id,
        data=payload.data,
        respondent_email=payload.respondent_email or None,
        payment_id=payload.payment_id or None,
        payment_amount=payload.payment_amount if payload.payment_amount is not None else None,
        payment_status="pending" if payload.payment_id else "none",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    if not form.razorpay_enabled:
        from backend.config import ADMIN_EMAIL
        try:
            if payload.respondent_email:
                send_notification(
                    to_email=payload.respondent_email,
                    form_title=form.title,
                    submission_data=payload.data,
                    form_id=form.id,
                    submission_id=submission.id,
                )
            
            target_email = form.notification_email or ADMIN_EMAIL
            if target_email:
                send_admin_notification(
                    admin_email=target_email,
                    form_title=form.title,
                    submission_data=payload.data,
                    form_id=form.id,
                    submission_id=submission.id,
                )
        except Exception as e:
            logger.error("Email notification error: %s", str(e))

    return submission


@router.get("/{form_id}/submissions", response_model=list[SubmissionResponse])
def list_submissions(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form or form.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    submissions = (
        db.query(Submission)
        .filter(Submission.form_id == form.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return submissions


@router.get(
    "/{form_id}/submissions/{submission_id}",
    response_model=SubmissionResponse,
)
def get_submission(form_id: str, submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form or form.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.form_id == form.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


import os
import shutil
import uuid

@router.post("/{form_id}/upload", status_code=201)
def upload_file(
    form_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    form = get_form_by_id_or_slug(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Ensure uploads dir exists
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Prevent path traversal and collisions
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error("Failed to save file: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to save file")
        
    return {"url": f"/uploads/{safe_filename}"}

@router.delete(
    "/{form_id}/submissions/{submission_id}",
    response_model=MessageResponse,
)
def delete_submission(form_id: str, submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form or form.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.form_id == form.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db.delete(submission)
    db.commit()
    return MessageResponse(message="Submission deleted successfully")
