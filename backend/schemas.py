from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---- Field Schemas ----

class FormField(BaseModel):
    id: str
    type: str
    label: str
    placeholder: str = ""
    required: bool = False
    options: list[str] = []
    order: int = 0


# ---- Form Schemas ----

class FormCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = ""
    fields: list[FormField] = []
    razorpay_enabled: bool = False
    razorpay_key_id: Optional[str] = ""
    razorpay_key_secret: Optional[str] = ""
    notification_email: Optional[str] = ""
    submit_button_text: str = "Submit"
    redirect_url: Optional[str] = ""


class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[list[FormField]] = None
    razorpay_enabled: Optional[bool] = None
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    notification_email: Optional[str] = None
    submit_button_text: Optional[str] = None
    redirect_url: Optional[str] = None
    is_active: Optional[bool] = None


class FormResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    fields: list[FormField] | list[dict[str, Any]]
    razorpay_enabled: bool
    razorpay_key_id: Optional[str]
    notification_email: Optional[str]
    submit_button_text: str
    redirect_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FormListItem(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_active: bool
    razorpay_enabled: bool
    submission_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Submission Schemas ----

class SubmissionCreate(BaseModel):
    data: dict[str, Any]
    respondent_email: Optional[str] = None
    payment_id: Optional[str] = None
    payment_amount: Optional[float] = None


class SubmissionResponse(BaseModel):
    id: int
    form_id: int
    data: dict[str, Any]
    respondent_email: Optional[str]
    payment_id: Optional[str]
    payment_status: str
    payment_amount: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Payment Schemas ----

class PaymentOrderRequest(BaseModel):
    amount: int
    currency: str = "INR"


class PaymentOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    submission_id: Optional[int] = None


class PaymentVerifyResponse(BaseModel):
    status: str
    message: str


# ---- Generic Response ----

class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ---- User Schemas ----

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    username: str


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None
    current_password: str = Field(..., min_length=6, max_length=100)
    new_password: Optional[str] = Field(None, min_length=6, max_length=100)
