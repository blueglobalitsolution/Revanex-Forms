import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Form, Submission, User
from backend.routes.auth import get_current_user
from backend.schemas import SubmissionCreate, SubmissionResponse, MessageResponse
from backend.services.email_service import send_notification, send_admin_notification

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/forms", tags=["submissions"])


@router.post("/{form_id}/submit", response_model=SubmissionResponse, status_code=201)
def submit_form(
    form_id: int,
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
):
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if not form.is_active:
        raise HTTPException(status_code=400, detail="This form is no longer accepting submissions")

    submission = Submission(
        form_id=form_id,
        data=payload.data,
        respondent_email=payload.respondent_email or None,
        payment_id=payload.payment_id or None,
        payment_amount=payload.payment_amount or None,
        payment_status="captured" if payload.payment_id else "none",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    try:
        if payload.respondent_email:
            send_notification(
                to_email=payload.respondent_email,
                form_title=form.title,
                submission_data=payload.data,
                form_id=form.id,
                submission_id=submission.id,
            )
        if form.notification_email:
            send_admin_notification(
                admin_email=form.notification_email,
                form_title=form.title,
                submission_data=payload.data,
                form_id=form.id,
                submission_id=submission.id,
            )
    except Exception as e:
        logger.error("Email notification error: %s", str(e))

    return submission


@router.get("/{form_id}/submissions", response_model=list[SubmissionResponse])
def list_submissions(form_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    submissions = (
        db.query(Submission)
        .filter(Submission.form_id == form_id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return submissions


@router.get(
    "/{form_id}/submissions/{submission_id}",
    response_model=SubmissionResponse,
)
def get_submission(form_id: int, submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.form_id == form_id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.delete(
    "/{form_id}/submissions/{submission_id}",
    response_model=MessageResponse,
)
def delete_submission(form_id: int, submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.form_id == form_id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db.delete(submission)
    db.commit()
    return MessageResponse(message="Submission deleted successfully")
