from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import create_access_token, hash_password, verify_password
from app.core.database import get_mongodb
from app.auth.schemas import UserCreate, UserLogin, Token, UserResponse, PasswordChange
from app.auth.models import UserInDB
from app.auth.service import get_user_by_username, get_user_by_email, create_user, authenticate_user
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate):
    existing_user = await get_user_by_username(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    
    existing_email = await get_user_by_email(user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
        
    user = await create_user(user_in)
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        cover_photo_url=user.cover_photo_url,
        bio=user.bio,
        website=user.website,
        social_links=user.social_links,
        is_verified=user.is_verified,
        credit_balance=user.credit_balance,
        follower_count=user.follower_count,
        following_count=user.following_count,
        created_at=user.created_at
    )

@router.post("/signin", response_model=Token)
async def signin(credentials: UserLogin):
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        cover_photo_url=current_user.cover_photo_url,
        bio=current_user.bio,
        website=current_user.website,
        social_links=current_user.social_links,
        is_verified=current_user.is_verified,
        credit_balance=current_user.credit_balance,
        follower_count=current_user.follower_count,
        following_count=current_user.following_count,
        created_at=current_user.created_at
    )

@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChange,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong old password"
        )
        
    db = await get_mongodb()
    new_hashed = hash_password(payload.new_password)
    await db.users.update_one(
        {"username": current_user.username},
        {"$set": {"hashed_password": new_hashed}}
    )
