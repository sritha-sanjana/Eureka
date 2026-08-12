from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import PyJWTError
import hashlib
import secrets
from backend.app.core.config import settings

# Support both token from Cookie and Bearer Authorization Header
cookie_sec = APIKeyCookie(name="admin_token", auto_error=False)
bearer_sec = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against an OWASP-compliant PBKDF2-SHA256 salted hash."""
    try:
        if not hashed_password or "$" not in hashed_password:
            return False
        salt, key = hashed_password.split("$")
        new_key = hashlib.pbkdf2_hmac(
            'sha256', 
            plain_password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        ).hex()
        return secrets.compare_digest(new_key, key)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generates an OWASP-compliant PBKDF2-SHA256 salted hash."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()
    return f"{salt}${key}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token using PyJWT."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # PyJWT expects standard integer unix timestamps for standard claims like 'exp'
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp())
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_admin(
    request: Request,
    cookie_token: Optional[str] = Depends(cookie_sec),
    bearer_token: Optional[HTTPAuthorizationCredentials] = Depends(bearer_sec)
) -> str:
    """
    Validates user session as Admin.
    Checks Authorization: Bearer token first, then fallback to cookies.
    """
    token = None
    if bearer_token:
        token = bearer_token.credentials
    elif cookie_token:
        token = cookie_token
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role != "admin":
            raise credentials_exception
        return username
    except PyJWTError:
        raise credentials_exception
