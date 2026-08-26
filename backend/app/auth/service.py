from datetime import datetime
from app.core.database import get_mongodb
from app.core.security import hash_password, verify_password
from app.auth.models import UserInDB
from app.auth.schemas import UserCreate

async def get_user_by_username(username: str) -> UserInDB | None:
    db = await get_mongodb()
    user_dict = await db.users.find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
    return None

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
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": hashed,
        "full_name": user_in.full_name,
        "avatar_url": None,
        "cover_photo_url": None,
        "bio": None,
        "website": None,
        "social_links": {"tiktok": None, "youtube": None},
        "is_verified": False,
        "credit_balance": 10,  # 10 free credits upon sign up
        "follower_count": 0,
        "following_count": 0,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    # Initialize default wallet log or transaction if needed
    # Create billing log
    credit_log = {
        "user_id": result.inserted_id,
        "amount": 10,
        "reason": "Welcome free credits on sign up",
        "created_at": datetime.utcnow()
    }
    await db.credit_logs.insert_one(credit_log)
    
    return UserInDB(**user_data)

async def authenticate_user(username: str, password: str) -> UserInDB | None:
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
