from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from app.config import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    secret = settings.JWT_SECRET or settings.AUTH_JWT_SECRET
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.AUTH_JWT_ALG)
    return encoded_jwt

def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    secret = settings.JWT_REFRESH_SECRET or settings.AUTH_JWT_SECRET
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.AUTH_JWT_ALG)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any] | None:
    secret = settings.JWT_SECRET or settings.AUTH_JWT_SECRET
    try:
        decoded = jwt.decode(token, secret, algorithms=[settings.AUTH_JWT_ALG])
        if decoded.get("type") != "access":
            return None
        return decoded
    except InvalidTokenError:
        return None

def decode_refresh_token(token: str) -> dict[str, Any] | None:
    secret = settings.JWT_REFRESH_SECRET or settings.AUTH_JWT_SECRET
    try:
        decoded = jwt.decode(token, secret, algorithms=[settings.AUTH_JWT_ALG])
        if decoded.get("type") != "refresh":
            return None
        return decoded
    except InvalidTokenError:
        return None
