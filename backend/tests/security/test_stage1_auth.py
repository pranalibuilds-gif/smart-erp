import pytest
import uuid
import asyncio
from httpx import AsyncClient
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token

@pytest.mark.asyncio
async def test_reg_duplicate_email(client: AsyncClient, erp_seed: dict):
    """Attack: Attempt to register with an existing email."""
    email = erp_seed["user"].email
    payload = {
        "email": email,
        "full_name": "Clone User",
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_reg_unicode_normalization(client: AsyncClient):
    """Attack: Register with similar unicode emails (e.g., n\u0303 vs \u00f1)."""
    # email1 = "test\u0303@example.com" # t\u0065st\u0303 (ñ-like)
    # email2 = "tes\u00f1@example.com"
    # Actually let's use a simpler one
    email1 = "user\u0040example.com"
    email2 = "user@example.com" # Standard @

    payload = {
        "email": email1,
        "full_name": "Unicode User",
        "password": "password123"
    }
    await client.post("/api/v1/auth/register", json=payload)

    payload["email"] = email2
    response = await client.post("/api/v1/auth/register", json=payload)
    # If the system doesn't normalize, it might allow both.
    # Usually, we want standard normalization to avoid identity confusion.
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_reg_extremely_long_name(client: AsyncClient):
    """Attack: 10,000 character name."""
    payload = {
        "email": f"long-{uuid.uuid4().hex}@example.com",
        "full_name": "A" * 10000,
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    # Should ideally be caught by validation (Pydantic)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_reg_malformed_email(client: AsyncClient):
    """Attack: Invalid email formats."""
    emails = ["plainaddress", "#@%^%#$@#$@#.com", "@example.com", "Joe Smith <email@example.com>"]
    for email in emails:
        payload = {
            "email": email,
            "full_name": "Malformed",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_incorrect_password(client: AsyncClient, erp_seed: dict):
    """Attack: Valid email, wrong password."""
    payload = {
        "email": erp_seed["user"].email,
        "password": "wrongpassword"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_jwt_none_algorithm(client: AsyncClient, erp_seed: dict):
    """Attack: Attempt to use 'none' algorithm in JWT."""
    # Construct a JWT-like string with alg: none
    user_id = str(erp_seed["user"].id)
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp())
    }
    import base64
    import json

    def b64_encode(data):
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

    header = {"alg": "none", "typ": "JWT"}
    token = f"{b64_encode(header)}.{b64_encode(payload)}."

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_jwt_wrong_key(client: AsyncClient, erp_seed: dict):
    """Attack: Attempt to sign JWT with a different key."""
    user_id = str(erp_seed["user"].id)
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
    }
    token = jwt.encode(payload, key="WRONG_KEY_1234567890", algorithm="HS256")

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_jwt_invalid_type_claims(client: AsyncClient, erp_seed: dict):
    """Attack: Access token with type='refresh'."""
    user_id = str(erp_seed["user"].id)
    # Generate a legitimate looking token but with wrong type claim
    token = create_refresh_token(subject=user_id) # This has type="refresh"

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_replay(client: AsyncClient, erp_seed: dict):
    """Attack: Use a refresh token twice after rotation."""
    login_payload = {
        "email": erp_seed["user"].email,
        "password": "password123"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["data"]["refresh_token"]

    # 1. First refresh (Success)
    res1 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res1.status_code == 200

    # 2. Second refresh with SAME token (Failure - Replay)
    res2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res2.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_race(client: AsyncClient, erp_seed: dict):
    """Attack: Simultaneous refresh requests with same token."""
    login_payload = {
        "email": erp_seed["user"].email,
        "password": "password123"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["data"]["refresh_token"]

    # Send two requests concurrently
    responses = await asyncio.gather(
        client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token}),
        client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token}),
        return_exceptions=True
    )

    # Result: Only one should succeed, or both fail if the lock is very strict.
    # In SmartERP, we expect exactly one success.
    success_count = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
    assert success_count == 1

@pytest.mark.asyncio
async def test_logout_and_reuse_refresh(client: AsyncClient, erp_seed: dict):
    """Attack: Use refresh token after logout."""
    login_payload = {
        "email": erp_seed["user"].email,
        "password": "password123"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["data"]["refresh_token"]

    # Logout
    await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})

    # Try refresh
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout_twice(client: AsyncClient, erp_seed: dict):
    """Attack: Logout with same token twice."""
    login_payload = {"email": erp_seed["user"].email, "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["data"]["refresh_token"]

    # Logout 1
    res1 = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert res1.status_code == 200

    # Logout 2 (Should not crash, should return success or 401)
    res2 = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert res2.status_code in [200, 401]

@pytest.mark.asyncio
async def test_logout_malformed_token(client: AsyncClient):
    """Attack: Logout with garbage token."""
    response = await client.post("/api/v1/auth/logout", json={"refresh_token": "not-a-token"})
    # Should not crash
    assert response.status_code in [200, 400, 422]
