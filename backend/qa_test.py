import requests
import random
import string
import json

BASE_URL = "http://127.0.0.1:8000"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_tests():
    print("--- STARTING QA TESTS ---")
    
    # 0. Health Check
    try:
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        print("[PASS] Health Check")
    except Exception as e:
        print(f"[FAIL] Health Check: {e}")
        return

    # 1. Setup User
    username = f"testuser_{generate_random_string(5)}"
    email = f"{username}@test.com"
    password = "Password123"
    full_name = "Test User"
    
    # Sign up
    r_signup = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name
    })
    
    if r_signup.status_code != 201:
        print(f"[FATAL] Setup - Signup failed: {r_signup.text}")
        return
        
    user_id = r_signup.json()["id"]
    print(f"[INFO] Created Test User: {username}, ID: {user_id}")

    # Sign in
    r_signin = requests.post(f"{BASE_URL}/auth/signin", json={
        "username": username,
        "password": password
    })
    
    if r_signin.status_code != 200:
        print(f"[FATAL] Setup - Signin failed: {r_signin.text}")
        return
        
    token = r_signin.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ==========================================
    # TEST SUITE 1: GET /auth/me
    # ==========================================
    print("\n--- Testing GET /auth/me ---")
    
    # TC 1.1: Valid Token
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if r.status_code == 200:
        data = r.json()
        assert data["username"] == username
        assert data["credit_balance"] == 10  # from our default logic
        print("[PASS] GET /auth/me (Valid Token)")
    else:
        print(f"[FAIL] GET /auth/me (Valid Token): {r.status_code} - {r.text}")

    # TC 1.2: No Token
    r = requests.get(f"{BASE_URL}/auth/me")
    if r.status_code in [401, 403]:
        print("[PASS] GET /auth/me (No Token)")
    else:
        print(f"[FAIL] GET /auth/me (No Token): expected 401/403, got {r.status_code}")

    # TC 1.3: Invalid Token
    r = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": "Bearer invalid_token_xyz"})
    if r.status_code in [401, 403]:
        print("[PASS] GET /auth/me (Invalid Token)")
    else:
        print(f"[FAIL] GET /auth/me (Invalid Token): expected 401/403, got {r.status_code}")

    # ==========================================
    # TEST SUITE 2: PATCH /auth/me
    # ==========================================
    print("\n--- Testing PATCH /auth/me ---")
    
    # TC 2.1: Valid Update (Full Name)
    new_name = "Updated Name"
    r = requests.patch(f"{BASE_URL}/auth/me", headers=headers, json={"full_name": new_name})
    if r.status_code == 200 and r.json()["full_name"] == new_name:
        print("[PASS] PATCH /auth/me (Valid full_name update)")
    else:
        print(f"[FAIL] PATCH /auth/me (Valid full_name update): {r.status_code} - {r.text}")

    # TC 2.2: Valid Update (Avatar URL)
    new_avatar = "https://example.com/avatar.png"
    r = requests.patch(f"{BASE_URL}/auth/me", headers=headers, json={"avatar_url": new_avatar})
    if r.status_code == 200 and r.json()["avatar_url"] == new_avatar:
        print("[PASS] PATCH /auth/me (Valid avatar_url update)")
    else:
        print(f"[FAIL] PATCH /auth/me (Valid avatar_url update): {r.status_code} - {r.text}")

    # TC 2.3: Attempt to inject unallowed fields (e.g. credit_balance)
    # The schema only accepts full_name and avatar_url, pydantic should ignore or reject others.
    r = requests.patch(f"{BASE_URL}/auth/me", headers=headers, json={
        "full_name": "Hacker",
        "credit_balance": 9999
    })
    
    # Verify the credit_balance was NOT updated
    r_check = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if r_check.json()["credit_balance"] == 10:
        print("[PASS] PATCH /auth/me (Ignored unallowed fields - Security Check)")
    else:
        print("[FAIL] PATCH /auth/me (Security breach! credit_balance updated)")

    # TC 2.4: Empty payload
    r = requests.patch(f"{BASE_URL}/auth/me", headers=headers, json={})
    if r.status_code == 200:
        print("[PASS] PATCH /auth/me (Empty payload - No crash)")
    else:
        print(f"[FAIL] PATCH /auth/me (Empty payload): {r.status_code} - {r.text}")

    # ==========================================
    # TEST SUITE 3: GET /users/{userId}
    # ==========================================
    print("\n--- Testing GET /users/{userId} ---")

    # TC 3.1: Valid ID
    r = requests.get(f"{BASE_URL}/users/{user_id}")
    if r.status_code == 200:
        data = r.json()
        if "email" not in data and "credit_balance" not in data and data["id"] == user_id:
            print("[PASS] GET /users/{userId} (Valid ID - Sensitive data hidden)")
        else:
            print(f"[FAIL] GET /users/{{userId}} (Data leak): {data}")
    else:
        print(f"[FAIL] GET /users/{{userId}} (Valid ID): {r.status_code} - {r.text}")

    # TC 3.2: Invalid ID format (Non-ObjectId string)
    invalid_id = "123_invalid_id"
    r = requests.get(f"{BASE_URL}/users/{invalid_id}")
    if r.status_code == 404:
        print("[PASS] GET /users/{userId} (Invalid format string - Graceful 404)")
    elif r.status_code >= 500:
        print(f"[FAIL] GET /users/{{userId}} (Invalid format string - SERVER CRASH): {r.status_code}")
    else:
        print(f"[FAIL] GET /users/{{userId}} (Invalid format string): {r.status_code}")

    # TC 3.3: Non-existent valid ObjectId
    not_found_id = "507f1f77bcf86cd799439011"
    r = requests.get(f"{BASE_URL}/users/{not_found_id}")
    if r.status_code == 404:
        print("[PASS] GET /users/{userId} (Non-existent ObjectId - 404)")
    else:
        print(f"[FAIL] GET /users/{{userId}} (Non-existent ObjectId): {r.status_code}")

    print("\n--- QA TESTS COMPLETED ---")

if __name__ == "__main__":
    run_tests()
