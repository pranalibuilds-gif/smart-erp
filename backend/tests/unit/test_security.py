import pytest
from datetime import timedelta
from jose import jwt, JWTError
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token
)
from app.core.config import settings

def test_password_hashing():
    password = "secret_password"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_token_hashing():
    token = "opaque_refresh_token"
    hashed1 = hash_token(token)
    hashed2 = hash_token(token)

    assert hashed1 == hashed2
    assert hashed1 != token

def test_create_access_token():
    subject = "user-123"
    token = create_access_token(subject)

    decoded = decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["type"] == "access"
    assert "exp" in decoded
    assert "iat" in decoded

def test_create_refresh_token():
    subject = "user-456"
    token = create_refresh_token(subject)

    decoded = decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["type"] == "refresh"

def test_invalid_token():
    with pytest.raises(JWTError):
        decode_token("invalid.token.string")

def test_expired_token():
    # This requires manually creating an expired token
    from datetime import datetime, timezone

    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = {"exp": expire, "sub": "test", "type": "access"}
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(JWTError):
        decode_token(token)

def test_token_type_differentiation():
    access = create_access_token("u1")
    refresh = create_refresh_token("u1")

    assert decode_token(access)["type"] == "access"
    assert decode_token(refresh)["type"] == "refresh"
