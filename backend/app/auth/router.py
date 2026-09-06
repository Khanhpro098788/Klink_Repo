import time
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    create_access_token, hash_password, verify_password, 
    create_refresh_token, decode_access_token, decode_refresh_token, create_reset_password_token
)
from app.core.database import get_mongodb
from app.auth.schemas import (
    UserCreate, UserLogin, Token, UserResponse, PasswordChange, UserUpdate, 
    ForgotPasswordRequest, ResetPasswordRequest, VerifyOtpRequest,
    GoogleAuthRequest, SendOTPRequest, VerifyOTPRequest, GoogleLoginRequest
)
from app.auth.models import UserInDB
from app.auth.service import get_user_by_email, create_user, authenticate_user, create_otp, verify_otp_service, verify_google_token, get_or_create_google_user, get_user_by_username
from app.auth.dependencies import get_current_user
from app.auth.otp_service import create_and_store_otp, verify_and_get_otp_data
from google.oauth2 import id_token
from google.auth.transport import requests
import uuid
from app.auth.utils import send_otp_email_async
from app.core.redis import is_rate_limited, redis_client, memory_cache
from bson import ObjectId

# Google Client ID
GOOGLE_CLIENT_ID = "361539172913-nksh7dk9s7bj2e39jnvtp4077hna3n5c.apps.googleusercontent.com" # Client will be verified

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, background_tasks: BackgroundTasks):
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
        
    user = await create_user(user_in)
    
    # Generate and send OTP code in the background
    otp_code = await create_otp(user.email)
    background_tasks.add_task(send_otp_email_async, user.email, otp_code)
    
    db = await get_mongodb()
    wallet = await db.wallets.find_one({"user_id": ObjectId(user.id)})
    balance = wallet["credit_balance"] if wallet else 10
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        cover_photo_url=user.cover_photo_url,
        bio=user.bio,
        website=user.website,
        social_links=user.social_links,
        is_verified=user.is_verified,
        credit_balance=balance,
        follower_count=user.follower_count,
        following_count=user.following_count,
        created_at=user.created_at
    )

@router.post("/token", response_model=Token)
async def login_for_access_token(
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
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(access_token=access_token)

@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(payload: SendOTPRequest, background_tasks: BackgroundTasks):
    # Check rate limit: max 5 requests per 10 minutes per email
    key = f"rate_limit:otp:{payload.email}"
    if await is_rate_limited(key, limit=5, period_seconds=600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please try again in 10 minutes."
        )
        
    user = await get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered"
        )
        
    otp_code = await create_otp(payload.email)
    background_tasks.add_task(send_otp_email_async, payload.email, otp_code)
    return {"message": "Verification code sent successfully"}

@router.post("/verify-otp", response_model=Token)
async def verify_otp(payload: VerifyOTPRequest, response: Response):
    # Rate limit OTP verification to prevent brute-forcing
    rate_key = f"rate_limit:verify_otp:{payload.email}"
    if await is_rate_limited(rate_key, limit=5, period_seconds=600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification attempts. Please try again in 10 minutes."
        )
        
    user = await verify_otp_service(payload.email, payload.otp_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or expired verification code for {payload.email}"
        )
        
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Set HttpOnly refresh token cookie
    from app.config import settings
    secure_cookie = settings.ENVIRONMENT != "local"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=30 * 24 * 3600  # 30 days
    )
    
    return Token(access_token=access_token)

@router.post("/google", response_model=Token)
async def google_login(payload: GoogleLoginRequest, response: Response):
    id_info = await verify_google_token(payload.google_token)
    if not id_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google credentials token"
        )
        
    user = await get_or_create_google_user(id_info)
    if not user.is_active:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Inactive user"
         )
         
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Set HttpOnly refresh token cookie
    from app.config import settings
    secure_cookie = settings.ENVIRONMENT != "local"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=30 * 24 * 3600  # 30 days
    )
    
    return Token(access_token=access_token)

@router.post("/signin", response_model=Token)
async def signin(credentials: UserLogin, response: Response):
    # Check brute force rate limit: max 10 failed login attempts per hour
    key = f"rate_limit:signin:{credentials.email}"
    blocked = False
    try:
        count = await redis_client.get(key)
        if count and int(count) >= 10:
            blocked = True
    except Exception:
        # Fallback to local memory cache block check
        data = memory_cache.get(key)
        if data and data.get("expires_at", 0) >= time.time() and data["count"] >= 10:
            blocked = True
            
    if blocked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again in 1 hour."
        )
        
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        # Increment failed login block count
        await is_rate_limited(key, limit=10, period_seconds=3600)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Clear the failed attempts block on successful login
    try:
        await redis_client.delete(key)
    except Exception:
        memory_cache.pop(key, None)
    
    # Check email verification
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
        
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Set HttpOnly refresh token cookie
    from app.config import settings
    secure_cookie = settings.ENVIRONMENT != "local"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=30 * 24 * 3600  # 30 days
    )
    
    return Token(access_token=access_token)

@router.post("/google/legacy", response_model=Token)
async def google_auth_legacy(
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

@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax"
    )

@router.post("/refresh", response_model=Token)
async def refresh(response: Response, refresh_token: Annotated[str | None, Cookie()] = None):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = await get_user_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    new_access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=new_access_token)
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    db = await get_mongodb()
    wallet = await db.wallets.find_one({"user_id": ObjectId(current_user.id)})
    balance = wallet["credit_balance"] if wallet else 0
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        cover_photo_url=current_user.cover_photo_url,
        bio=current_user.bio,
        website=current_user.website,
        social_links=current_user.social_links,
        is_verified=current_user.is_verified,
        credit_balance=balance,
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
    if not current_user.password_hash or not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong old password"
        )
        
    db = await get_mongodb()
    new_hashed = hash_password(payload.new_password)
    await db.users.update_one(
        {"email": current_user.email},
        {"$set": {"password_hash": new_hashed}}
    )
