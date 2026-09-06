from pydantic import BaseModel

class UserPublicResponse(BaseModel):
    id: str
    username: str
    full_name: str
    avatar_url: str | None = None

    class Config:
        from_attributes = True
