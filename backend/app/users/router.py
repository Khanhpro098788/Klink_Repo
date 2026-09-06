from fastapi import APIRouter, HTTPException, status
from app.users.schemas import UserPublicResponse
from app.users.service import get_user_by_id

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{userId}", response_model=UserPublicResponse)
async def get_user_profile(userId: str):
    user = await get_user_by_id(userId)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return UserPublicResponse(
        id=str(user.id),
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url
    )
