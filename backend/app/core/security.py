import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
import hashlib

from app.core.config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Returns the bcrypt hash of a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    """
    Hashes a token string for storage in the database.
    Uses SHA-256 for fast, deterministic hashing of opaque tokens.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def create_token(
    subject: Union[str, Any],
    expires_delta: timedelta,
    token_type: str
) -> str:
    """
    Base utility to create a JWT token.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": token_type,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()) # Ensure token uniqueness
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_access_token(subject: Union[str, Any]) -> str:
    """Generates a short-lived access token."""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, token_type="access")


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Generates a long-lived refresh token."""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(subject, expires_delta, token_type="refresh")


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises JWTError if invalid or expired.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
