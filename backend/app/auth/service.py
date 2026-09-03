from datetime import datetime, timedelta, UTC
from app.core.database import get_mongodb
from app.core.security import hash_password, verify_password
from app.auth.models import UserInDB
from app.auth.schemas import UserCreate
from app.auth.utils import generate_otp
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.config import settings
from fastapi.concurrency import run_in_threadpool
import uuid



async def get_user_by_email(email: str) -> UserInDB | None:
    db = await get_mongodb()
    user_dict = await db.users.find_one({"email": email})
    if user_dict:
        return UserInDB(**user_dict)
    return None

async def create_user(user_in: UserCreate) -> UserInDB:
    db = await get_mongodb()
    hashed = hash_password(user_in.password)
    
    user_data = {
        "email": user_in.email,
        "password_hash": hashed,
        "full_name": user_in.full_name,
        "avatar_url": None,
        "cover_photo_url": None,
        "bio": None,
        "website": None,
        "social_links": {"tiktok": None, "youtube": None},
        "is_verified": False,
        "is_email_verified": False,
        "auth_provider": "local",
        "follower_count": 0,
        "following_count": 0,
        "is_active": True,
        "created_at": datetime.now(UTC).replace(tzinfo=None),
        "updated_at": datetime.now(UTC).replace(tzinfo=None)
    }
    
    result = await db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    # Initialize default wallet in wallets collection
    wallet_data = {
        "user_id": result.inserted_id,
        "credit_balance": 10
    }
    await db.wallets.insert_one(wallet_data)
    
    # Create billing log
    credit_log = {
        "user_id": result.inserted_id,
        "amount": 10,
        "reason": "Welcome free credits on sign up",
        "created_at": datetime.now(UTC).replace(tzinfo=None)
    }
    await db.credit_logs.insert_one(credit_log)
    
    return UserInDB(**user_data)
 
async def authenticate_user(email: str, password: str) -> UserInDB | None:
    user = await get_user_by_email(email)
    if not user:
        return None
    if not user.password_hash or not verify_password(password, user.password_hash):
        return None
    return user

async def create_otp(email: str) -> str:
    db = await get_mongodb()
    otp_code = generate_otp()
    expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=5)
    
    # Mark old unused OTPs for this email as used/invalidated
    await db.otps.update_many(
        {"email": email, "is_used": False},
        {"$set": {"is_used": True}}
    )
    
    await db.otps.insert_one({
        "email": email,
        "otp_code": otp_code,
        "expires_at": expires_at,
        "is_used": False
    })
    return otp_code

async def verify_otp_service(email: str, otp_code: str) -> UserInDB | None:
    db = await get_mongodb()
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Find matching unused OTP that hasn't expired
    otp = await db.otps.find_one({
        "email": email,
        "otp_code": otp_code,
        "is_used": False,
        "expires_at": {"$gt": now}
    })
    
    if not otp:
        return None
        
    # Mark OTP as used
    await db.otps.update_one(
        {"_id": otp["_id"]},
        {"$set": {"is_used": True}}
    )
    
    # Verify user's email
    update_result = await db.users.update_one(
        {"email": email},
        {"$set": {"is_email_verified": True}}
    )
    if update_result.matched_count == 0:
        return None
        
    user = await get_user_by_email(email)
    return user

async def verify_google_token(token: str) -> dict | None:
    """Verifies Google ID token and returns payload if valid, otherwise None."""
    try:
        # verify_oauth2_token is blocking, so we run it in a threadpool
        id_info = await run_in_threadpool(
            id_token.verify_oauth2_token,
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        return id_info
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Google token verification failed: {e}")
        return None

async def get_or_create_google_user(payload: dict) -> UserInDB:
    db = await get_mongodb()
    email = payload.get("email")
    name = payload.get("name", "Google User")
    picture = payload.get("picture")
    
    # 1. Try finding existing user by email
    user = await get_user_by_email(email)
    if user:
        if not user.is_email_verified or user.auth_provider != "google":
            await db.users.update_one(
                {"email": email},
                {"$set": {"is_email_verified": True, "auth_provider": "google"}}
            )
            user.is_email_verified = True
            user.auth_provider = "google"
        return user
        
    # 2. Create new user document
    user_data = {
        "email": email,
        "password_hash": None,
        "full_name": name,
        "avatar_url": picture,
        "cover_photo_url": None,
        "bio": None,
        "website": None,
        "social_links": {"tiktok": None, "youtube": None},
        "is_verified": False,
        "is_email_verified": True,
        "auth_provider": "google",
        "follower_count": 0,
        "following_count": 0,
        "is_active": True,
        "created_at": datetime.now(UTC).replace(tzinfo=None),
        "updated_at": datetime.now(UTC).replace(tzinfo=None)
    }
    
    result = await db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    # 4. Initialize Wallet in wallets collection with 10 credits
    wallet_data = {
        "user_id": result.inserted_id,
        "credit_balance": 10
    }
    await db.wallets.insert_one(wallet_data)
    
    # 5. Create billing log for credit initialization
    credit_log = {
        "user_id": result.inserted_id,
        "amount": 10,
        "reason": "Welcome free credits on Google sign up",
        "created_at": datetime.now(UTC).replace(tzinfo=None)
    }
    await db.credit_logs.insert_one(credit_log)
    
    return UserInDB(**user_data)
