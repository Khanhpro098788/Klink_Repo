from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.auth.models import SocialLinks

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)

class UserLogin(BaseModel):
    username: str
    password: str

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
    old_password: str
    new_password: str = Field(..., min_length=6)
