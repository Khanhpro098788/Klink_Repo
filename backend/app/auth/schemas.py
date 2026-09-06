from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.auth.models import SocialLinks

class UserCreate(BaseModel):
    email: EmailStr
    username: str | None = None
    password: str = Field(..., min_length=8, pattern="^([A-Za-z]+[0-9][A-Za-z0-9]*|[0-9]+[A-Za-z][A-Za-z0-9]*)$")
    full_name: str = Field(..., min_length=1, max_length=100)
    auth_provider: str = "local"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class GoogleAuthRequest(BaseModel):
    token: str

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str
    avatar_url: str | None = None
    cover_photo_url: str | None = None
    bio: str | None = None
    website: str | None = None
    social_links: SocialLinks
    is_verified: bool
    credit_balance: int
    follower_count: int
    following_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    old_password: str | None = None
    new_password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None
