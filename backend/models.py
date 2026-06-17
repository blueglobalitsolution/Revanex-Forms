from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, JSON, Float, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    forms = relationship("Form", back_populates="creator", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(255), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")


class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    fields = Column(JSON, nullable=False, default=list)
    razorpay_enabled = Column(Boolean, default=False)
    razorpay_key_id = Column(String(255), nullable=True)
    razorpay_key_secret = Column(String(255), nullable=True)
    notification_email = Column(String(255), nullable=True)
    submit_button_text = Column(String(100), default="Submit")
    redirect_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submissions = relationship(
        "Submission", back_populates="form", cascade="all, delete-orphan"
    )
    creator = relationship("User", back_populates="forms")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSON, nullable=False)
    respondent_email = Column(String(255), nullable=True)
    payment_id = Column(String(255), nullable=True)
    payment_status = Column(String(50), default="none")
    payment_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    form = relationship("Form", back_populates="submissions")
