from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    create_access_token, hash_password, verify_password, 
    create_refresh_token, decode_access_token, create_reset_password_token
)
from app.core.database import get_mongodb
from app.auth.schemas import (
    UserCreate, Token, UserResponse, PasswordChange, UserUpdate, 
    ForgotPasswordRequest, ResetPasswordRequest, VerifyOtpRequest,
    GoogleAuthRequest
)
from app.auth.models import UserInDB
from app.auth.service import get_user_by_username, get_user_by_email, create_user, authenticate_user
from app.auth.dependencies import get_current_user
from app.auth.otp_service import create_and_store_otp, verify_and_get_otp_data
from google.oauth2 import id_token
from google.auth.transport import requests
import uuid

# Google Client ID
GOOGLE_CLIENT_ID = "361539172913-nksh7dk9s7bj2e39jnvtp4077hna3n5c.apps.googleusercontent.com" # Client will be verified

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=status.HTTP_200_OK)
async def signup(user_in: UserCreate):
    if user_in.username:
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
        
    await create_and_store_otp(user_in.email, user_in.model_dump())
    
    return {"message": "Mã OTP đã được gửi đến email của bạn."}

@router.post("/verify-otp", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def verify_otp(payload: VerifyOtpRequest):
    user_data = await verify_and_get_otp_data(payload.email, payload.otp)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã OTP không hợp lệ hoặc đã hết hạn"
        )
        
    # Re-verify email just in case
    existing_email = await get_user_by_email(payload.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
        
    user_in = UserCreate(**user_data)
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
async def signin(
    response: Response,
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True, 
        secure=True, 
        samesite="lax", 
        max_age=30*24*60*60
    )
    return Token(access_token=access_token)

@router.post("/google", response_model=Token)
async def google_auth(
    response: Response,
    payload: GoogleAuthRequest
):
    try:
        # Verify token with Google, allow 60s clock skew because local computer time might be slightly behind
        idinfo = id_token.verify_oauth2_token(
            payload.token, 
            requests.Request(), 
            audience=GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=60
        )
        
        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")
        
        if not email:
            raise HTTPException(status_code=400, detail="Google auth did not return an email")
            
        user = await get_user_by_email(email)
        
        if not user:
            # Create a new user automatically
            generated_password = str(uuid.uuid4())
            user_in = UserCreate(
                email=email,
                full_name=name or "Google User",
                password=generated_password
            )
            user = await create_user(user_in)
            
            # Optionally update avatar
            if picture:
                db = await get_mongodb()
                await db.users.update_one(
                    {"email": email},
                    {"$set": {"avatar_url": picture}}
                )
                
        # Generate tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token, 
            httponly=True, 
            secure=True, 
            samesite="lax", 
            max_age=30*24*60*60
        )
        return Token(access_token=access_token)
        
    except ValueError as e:
        print(f"Google Token Verification Error: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {e}")

@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: Annotated[str | None, Cookie()] = None):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
        
    payload = decode_access_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    username = payload.get("sub")
    user = await get_user_by_username(username)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or deleted user")
        
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)

@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(response: Response):
    response.delete_cookie(key="refresh_token")
    return None

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest):
    user = await get_user_by_email(payload.email)
    if user:
        reset_token = create_reset_password_token(payload.email)
        # Mock sending email by printing to terminal
        print(f"--- MOCK EMAIL ---")
        print(f"To: {payload.email}")
        print(f"Subject: Reset your password")
        print(f"Token: {reset_token}")
        print(f"------------------")
    return {"message": "If that email is in our database, we will send a reset link."}

@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(payload: ResetPasswordRequest):
    decoded = decode_access_token(payload.token)
    if not decoded or decoded.get("type") != "reset_password":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
        
    email = decoded.get("sub")
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        
    db = await get_mongodb()
    new_hashed = hash_password(payload.new_password)
    await db.users.update_one(
        {"email": email},
        {"$set": {"hashed_password": new_hashed}}
    )

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

@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    db = await get_mongodb()
    update_data = {}
    if payload.full_name is not None:
        update_data["full_name"] = payload.full_name
    if payload.avatar_url is not None:
        update_data["avatar_url"] = payload.avatar_url
        
    if update_data:
        from datetime import datetime
        update_data["updated_at"] = datetime.utcnow()
        await db.users.update_one(
            {"username": current_user.username},
            {"$set": update_data}
        )
        
        # Refetch user to get the latest data
        current_user = await get_user_by_username(current_user.username)
            
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
