import random
import string
from datetime import datetime, timedelta
from app.core.database import get_mongodb
from app.auth.email_service import send_email_async

def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

async def create_and_store_otp(email: str, user_data: dict) -> str:
    """
    Generate OTP, store it in db with user_data, and return the OTP.
    TTL index will automatically expire this document after 5 minutes.
    """
    db = await get_mongodb()
    
    otp = generate_otp()
    
    otp_doc = {
        "email": email,
        "otp": otp,
        "user_data": user_data,
        "created_at": datetime.utcnow()
    }
    
    # Store or update if exists
    await db.otps.update_one(
        {"email": email},
        {"$set": otp_doc},
        upsert=True
    )
    
    # Send actual email
    subject = "Mã xác nhận (OTP) đăng ký tài khoản Klink AI"
    body = f"""Chào bạn,

Mã xác nhận OTP của bạn là: {otp}

Mã này sẽ hết hạn trong vòng 5 phút. Vui lòng không chia sẻ mã này cho bất kỳ ai.

Trân trọng,
Đội ngũ Klink AI
"""
    await send_email_async(email, subject, body)
    
    return otp

async def verify_and_get_otp_data(email: str, otp: str) -> dict | None:
    """
    Verify OTP and return the stored user_data if valid.
    """
    db = await get_mongodb()
    
    doc = await db.otps.find_one({"email": email, "otp": otp})
    if doc:
        # OTP is valid, optionally delete it so it can't be reused
        await db.otps.delete_one({"_id": doc["_id"]})
        return doc.get("user_data")
        
    return None

async def setup_otp_indexes():
    """Create TTL index for otps collection"""
    db = await get_mongodb()
    # Expire after 300 seconds (5 minutes)
    await db.otps.create_index([("created_at", 1)], expireAfterSeconds=300)
