import csv
import io
import logging
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Form, Submission, User
from backend.routes.auth import get_current_user
from backend.schemas import (
    FormCreate,
    FormUpdate,
    FormResponse,
    FormListItem,
    MessageResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/forms", tags=["forms"])


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def generate_unique_slug(db: Session, title: str, exclude_id: int | None = None) -> str:
    base_slug = slugify(title)
    if not base_slug:
        base_slug = "untitled"
    slug = base_slug
    counter = 1
    while True:
        query = db.query(Form).filter(Form.slug == slug)
        if exclude_id is not None:
            query = query.filter(Form.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


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


@router.get("", response_model=list[FormListItem])
def list_forms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    forms = db.query(Form).filter(Form.user_id == current_user.id).order_by(Form.created_at.desc()).all()
    result = []
    for form in forms:
        count = db.query(func.count(Submission.id)).filter(
            Submission.form_id == form.id
        ).scalar()
        result.append(FormListItem(
            id=form.id,
            title=form.title,
            description=form.description,
            is_active=form.is_active,
            razorpay_enabled=form.razorpay_enabled,
            submission_count=count,
            created_at=form.created_at,
        ))
    return result


@router.post("", response_model=FormResponse, status_code=201)
def create_form(payload: FormCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = Form(
        user_id=current_user.id,
        title=payload.title,
        slug=generate_unique_slug(db, payload.title),
        description=payload.description,
        fields=[f.model_dump() for f in payload.fields],
        razorpay_enabled=payload.razorpay_enabled,
        razorpay_key_id=payload.razorpay_key_id or None,
        razorpay_key_secret=payload.razorpay_key_secret or None,
        notification_email=payload.notification_email or None,
        submit_button_text=payload.submit_button_text,
        redirect_url=payload.redirect_url or None,
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    return form


@router.get("/{form_id}", response_model=FormResponse)
def get_form(form_id: str, db: Session = Depends(get_db)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form


@router.put("/{form_id}", response_model=FormResponse)
def update_form(form_id: str, payload: FormUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form or form.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    update_data = payload.model_dump(exclude_unset=True)
    if "fields" in update_data and update_data["fields"] is not None:
        update_data["fields"] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in update_data["fields"]]

    if "title" in update_data and update_data["title"]:
        update_data["slug"] = generate_unique_slug(db, update_data["title"], exclude_id=form.id)

    for key, value in update_data.items():
        setattr(form, key, value)

    db.commit()
    db.refresh(form)
    return form


@router.delete("/{form_id}", response_model=MessageResponse)
def delete_form(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form or form.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Form not found or access denied")
    db.delete(form)
    db.commit()
    return MessageResponse(message="Form deleted successfully")


@router.get("/{form_id}/embed")
def get_embed_code(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form or form.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Form not found or access denied")
    embed = (
        f'<iframe src="{form.id}" '
        f'width="100%" height="800" frameborder="0" '
        f'style="border:1px solid #e5e7eb;border-radius:8px;max-width:720px;margin:0 auto;display:block">'
        f"</iframe>"
    )
    return {"embed_code": embed, "direct_link": f"/f/{form.id}"}


@router.get("/{form_id}/submissions/export")
def export_submissions_csv(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = get_form_by_id_or_slug(db, form_id)
    if not form or form.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Form not found or access denied")

    submissions = (
        db.query(Submission)
        .filter(Submission.form_id == form.id)
        .order_by(Submission.created_at.desc())
        .all()
    )

    all_keys = ["submission_id", "submitted_at"]
    seen = set(all_keys)
    for sub in submissions:
        for key in sub.data.keys():
            if key not in seen:
                all_keys.append(key)
                seen.add(key)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(all_keys)

    for sub in submissions:
        row = [sub.id, sub.created_at.isoformat() if sub.created_at else ""]
        for key in all_keys[2:]:
            row.append(sub.data.get(key, ""))
        writer.writerow(row)

    output.seek(0)
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in form.title)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"{safe_title}_submissions.csv\""
        },
    )
