import asyncio
import httpx
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

BASE_URL = "http://127.0.0.1:8000/auth"
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "Mova")

async def run_tests():
    test_id = str(uuid.uuid4())[:8]
    test_email = f"qa_test_{test_id}@example.com"
    test_password = "password123"
    
    print(f"--- BẮT ĐẦU TEST AUTH (QA MODE) ---")
    print(f"Email test: {test_email}")
    
    client = httpx.AsyncClient(base_url=BASE_URL, timeout=15.0)
    
    try:
        # 1. SIGNUP
        print("\n[QA-01] Test /signup")
        res = await client.post("/signup", json={
            "email": test_email,
            "password": test_password,
            "full_name": "QA Tester"
        })
        print(f"Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == 201, f"Expected 201, got {res.status_code}"
        
        # 2. Get OTP from DB
        print("\n[QA-02] Fetching OTP from DB for verification...")
        mongo = AsyncIOMotorClient(MONGO_URI)
        db = mongo[DB_NAME]
        otp_doc = await db.otps.find_one({"email": test_email, "is_used": False}, sort=[("expires_at", -1)])
        
        if not otp_doc:
            print("❌ LỖI: Không tìm thấy OTP trong DB.")
            return
            
        otp_code = otp_doc["otp_code"]
        print(f"OTP Code: {otp_code}")
        
        # 3. VERIFY OTP
        print("\n[QA-03] Test /verify-otp")
        res = await client.post("/verify-otp", json={
            "email": test_email,
            "otp_code": otp_code
        })
        print(f"Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == 200, "Expected 200 on Verify OTP"
        
        # 4. SIGNIN
        print("\n[QA-04] Test /signin")
        res = await client.post("/signin", json={
            "email": test_email,
            "password": test_password
        })
        print(f"Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == 200, "Expected 200 on Signin"
        tokens = res.json()
        access_token = tokens["access_token"]
        refresh_cookie = res.cookies.get("refresh_token")
        print(f"Received access_token: {access_token[:15]}...")
        print(f"Received refresh_cookie: {refresh_cookie[:15]}...")
        
        # 5. GET ME
        print("\n[QA-05] Test /me")
        headers = {"Authorization": f"Bearer {access_token}"}
        res = await client.get("/me", headers=headers)
        print(f"Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == 200, "Expected 200 on Get Me"
        
        # 6. CHANGE PASSWORD
        print("\n[QA-06] Test /me/password")
        res = await client.patch("/me/password", headers=headers, json={
            "old_password": test_password,
            "new_password": "new_password123"
        })
        print(f"Status: {res.status_code}")
        assert res.status_code == 204, "Expected 204 on Change Password"
        
        # 7. SIGNIN WITH NEW PASSWORD
        print("\n[QA-07] Test /signin (New Password)")
        res = await client.post("/signin", json={
            "email": test_email,
            "password": "new_password123"
        })
        print(f"Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == 200, "Expected 200 on Signin with new password"
        
        # 8. REFRESH TOKEN
        print("\n[QA-08] Test /refresh")
        cookies = {"refresh_token": refresh_cookie}
        res = await client.post("/refresh", cookies=cookies)
        print(f"Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == 200, "Expected 200 on Refresh Token"
        
        # 9. SEND OTP AGAIN (Test Rate Limit)
        print("\n[QA-09] Test /send-otp")
        res = await client.post("/send-otp", json={
            "email": test_email
        })
        print(f"Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == 200, "Expected 200 on Send OTP"
        
        # 10. SIGNOUT
        print("\n[QA-10] Test /signout")
        res = await client.post("/signout")
        print(f"Status: {res.status_code}")
        assert res.status_code == 204, "Expected 204 on Signout"
        
        # Cleanup test user from DB
        print("\n[QA-11] Cleanup Database (Xóa dữ liệu user test để tránh rác DB)...")
        user = await db.users.find_one({"email": test_email})
        if user:
            user_id = user["_id"]
            await db.users.delete_one({"_id": user_id})
            await db.wallets.delete_one({"user_id": user_id})
            await db.otps.delete_many({"email": test_email})
            await db.credit_logs.delete_many({"user_id": user_id})
            print("Đã dọn dẹp sạch sẽ dữ liệu rác.")
            
        print("\n✅ TẤT CẢ TEST CASE ĐÃ PASS HOÀN HẢO!")
        
    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH TEST: {e}")
    finally:
        await client.aclose()
        mongo.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
