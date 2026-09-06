import pytest
import uuid
from bson import ObjectId
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_mongodb

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "klink-api-gateway"}

@pytest.mark.anyio
async def test_signup_validation_error(client: AsyncClient):
    response = await client.post("/auth/signup", json={"email": "invalid-email"})
    assert response.status_code == 422

@pytest.mark.anyio
async def test_mongodb_integration_flow(client: AsyncClient):
    # This test directly connects to the configured MongoDB (Atlas) database,
    # inserts a record, logs in to query it, and then performs cleanup.
    
    unique_id = uuid.uuid4().hex[:6]
    test_username = f"user_{unique_id}"
    test_email = f"user_{unique_id}@example.com"
    
    signup_payload = {
        "email": test_email,
        "password": "strong_test_password_123",
        "full_name": "Integration Test User"
    }
    
    # 1. Sign up (Writes to MongoDB Atlas)
    signup_response = await client.post("/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201
    user_data = signup_response.json()
    assert user_data["email"] == test_email
    assert user_data["credit_balance"] == 10  # Initial free credits
    
    user_id = user_data["id"]

    # Retrieve OTP code from database to verify email
    db = await get_mongodb()
    otp_doc = await db.otps.find_one({"email": test_email, "is_used": False})
    assert otp_doc is not None
    otp_code = otp_doc["otp_code"]

    # Verify OTP
    verify_response = await client.post("/auth/verify-otp", json={
        "email": test_email,
        "otp_code": otp_code
    })
    assert verify_response.status_code == 200
    assert "access_token" in verify_response.json()

    # 2. Sign in (Reads from MongoDB Atlas & Authenticates)
    signin_response = await client.post("/auth/signin", json={
        "email": test_email,
        "password": "strong_test_password_123"
    })
    assert signin_response.status_code == 200
    token_data = signin_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 3. Clean up database records from MongoDB Atlas to avoid bloating
    db = await get_mongodb()
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.wallets.delete_many({"user_id": ObjectId(user_id)})
    await db.credit_logs.delete_many({"user_id": ObjectId(user_id)})
    
    # Verify cleanup
    user_exists = await db.users.find_one({"_id": ObjectId(user_id)})
    assert user_exists is None
