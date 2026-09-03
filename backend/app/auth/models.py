from datetime import datetime
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, Field

# Represents ObjectId in MongoDB mapped to a string in Pydantic
PyObjectId = Annotated[str, BeforeValidator(str)]

class SocialLinks(BaseModel):
    tiktok: str | None = None
    youtube: str | None = None

class UserInDB(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    email: str
    password_hash: str | None = None
    full_name: str
    avatar_url: str | None = None
    cover_photo_url: str | None = None
    bio: str | None = None
    website: str | None = None
    social_links: SocialLinks = Field(default_factory=SocialLinks)
    is_verified: bool = False
    is_email_verified: bool = False
    auth_provider: str = "local"  # "local" or "google"
    follower_count: int = 0
    following_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WalletInDB(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    user_id: PyObjectId
    credit_balance: int = 10

class OTPInDB(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    email: str
    otp_code: str
    expires_at: datetime
    is_used: bool = False
