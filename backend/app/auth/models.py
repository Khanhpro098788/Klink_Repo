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
    username: str
    email: str
    hashed_password: str
    full_name: str
    avatar_url: str | None = None
    cover_photo_url: str | None = None
    bio: str | None = None
    website: str | None = None
    social_links: SocialLinks = Field(default_factory=SocialLinks)
    is_verified: bool = False
    credit_balance: int = 10  # default free credits
    follower_count: int = 0
    following_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
