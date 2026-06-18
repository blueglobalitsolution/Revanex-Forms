import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, UserSession, Form
from backend.schemas import UserCreate, UserResponse, MessageResponse, ForgotPasswordRequest, UserProfileUpdate

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Cookie settings
SESSION_COOKIE_NAME = "session_id"
SESSION_DURATION_DAYS = 7


# ---- Password Hashing Utilities ----

def hash_password(password: str) -> str:
    # PBKDF2 with SHA-256, 100,000 iterations
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt_hex, key_hex = hashed.split(":")
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return key.hex() == key_hex
    except Exception:
        return False


# ---- Session Utilities & Dependency ----

def create_session(user_id: int, db: Session) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=SESSION_DURATION_DAYS)
    
    session = UserSession(id=token, user_id=user_id, expires_at=expires_at)
    db.add(session)
    db.commit()
    return token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
        )
        
    session = db.query(UserSession).filter(UserSession.id == token).first()
    if not session or session.expires_at < datetime.utcnow():
        if session:
            # Delete expired session
            db.delete(session)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again.",
        )
        
    return session.user


# ---- Authentication API Routes ----

# Register endpoint removed for security. Accounts are seeded on startup or managed by admins.


@router.post("/login", response_model=UserResponse)
def login_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
        
    # Create session
    token = create_session(user.id, db)
    
    from backend.config import APP_URL

    is_https = APP_URL.startswith("https")

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=is_https,
    )
    
    return user


@router.post("/logout", response_model=MessageResponse)
def logout_user(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        session = db.query(UserSession).filter(UserSession.id == token).first()
        if session:
            db.delete(session)
            db.commit()
            
    from backend.config import APP_URL

    is_https = APP_URL.startswith("https")

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=is_https,
    )
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    
    success_msg = MessageResponse(message="If the username is valid, a temporary password email has been sent.")
    
    if not user:
        return success_msg
        
    # Generate temporary password
    temp_password = secrets.token_hex(6)  # 12 character alphanumeric
    user.hashed_password = hash_password(temp_password)
    db.commit()
    
    from backend.config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_NAME
    if SMTP_EMAIL and SMTP_PASSWORD:
        try:
            import yagmail
            yag = yagmail.SMTP({SMTP_EMAIL: SMTP_NAME}, SMTP_PASSWORD)
            html_body = f"""
            <div style="max-width:600px;margin:0 auto;font-family:Arial,sans-serif">
                <div style="background:#864d26;padding:24px;border-radius:12px 12px 0 0;text-align:center">
                    <h1 style="color:#fff;margin:0;font-size:22px">Password Reset Request</h1>
                </div>
                <div style="border:1px solid #fbfbf2;border-top:0;padding:24px;border-radius:0 0 12px 12px;background:#ffffff;color:#89868d">
                    <p>Hello <strong>{user.username}</strong>,</p>
                    <p>Your password has been reset. Use the temporary password below to log in:</p>
                    <div style="background:#fbfbf2;padding:16px;border-radius:10px;text-align:center;font-size:20px;font-weight:700;letter-spacing:1px;color:#864d26;margin:20px 0">
                        {temp_password}
                    </div>
                    <p style="color:#666666;font-size:14px">Please change your password immediately after logging in.</p>
                    <hr style="border:none;border-top:1px solid #fbfbf2;margin:20px 0">
                    <p style="font-size:12px;color:#666666;text-align:center">Revanex Forms</p>
                </div>
            </div>
            """
            recipient_email = user.email or SMTP_EMAIL
            yag.send(
                to=recipient_email,
                subject="Revanex Forms — Password Reset",
                contents=html_body
            )
        except Exception as e:
            print(f"Failed to send reset email: {e}")
    else:
        # Development fallback console logging
        print(f"\n[DEVELOPMENT RESET] Temporary password for user '{user.username}': {temp_password}\n")
        
    return success_msg


@router.put("/profile", response_model=UserResponse)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify current password
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password.",
        )
        
    # Update username if provided and changed
    if payload.username and payload.username.strip() != current_user.username:
        new_username = payload.username.strip()
        existing_user = db.query(User).filter(User.username == new_username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken.",
            )
        current_user.username = new_username
        
    # Update email if provided
    if payload.email is not None:
        current_user.email = payload.email.strip() or None
        
    # Update password if provided
    if payload.new_password:
        current_user.hashed_password = hash_password(payload.new_password)
        
    db.commit()
    db.refresh(current_user)
    return current_user
