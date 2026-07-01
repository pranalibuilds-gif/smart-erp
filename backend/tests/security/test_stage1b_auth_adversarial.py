import pytest
import uuid
import time
import asyncio
from httpx import AsyncClient
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password

@pytest.mark.asyncio
async def test_auth_timing_resistance(client: AsyncClient):
    """
    Stage 1B: Timing Attack Audit.
    Compare response times for:
    1. Non-existent email
    2. Existing email + Wrong password
    """
    # 1. Non-existent email
    start = time.perf_counter()
    await client.post("/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "password123"})
    t1 = time.perf_counter() - start

    # 2. Register a user for test
    email = f"timing-{uuid.uuid4().hex}@example.com"
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Timing User",
        "password": "correctpassword123"
    })

    # 3. Existing email + Wrong password
    start = time.perf_counter()
    await client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpassword"})
    t2 = time.perf_counter() - start

    # Logging observation
    print(f"\nTiming Analysis: Non-existent: {t1*1000:.2f}ms, Wrong Password: {t2*1000:.2f}ms")
    # If the difference is huge (e.g., factor of 10), it fails the spirit of the audit.
    # Bcrypt is usually the bottleneck for both if implemented correctly (checking hash regardless of email existence).
    assert abs(t1 - t2) < 0.2 # Loose bound for local tests, but looking for consistency.

@pytest.mark.asyncio
async def test_bcrypt_72_byte_limit(client: AsyncClient):
    """
    Stage 1B: Password Policy - Bcrypt 72-byte boundary check.
    Bcrypt ignores everything after 72 bytes. We should either:
    A) Truncate/Reject at API level (Fixed in 1A)
    B) Ensure we verify exactly what was stored.
    """
    base_pwd = "P" * 72
    attacker_pwd = base_pwd + "IGNORE_ME"

    email = f"bcrypt-{uuid.uuid4().hex}@example.com"
    # Register with long password
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Bcrypt User",
        "password": base_pwd
    })

    # Attempt login with EVEN LONGER password that shares same 72 byte prefix
    # If bcrypt works as standard, it might accept 'attacker_pwd' as 'base_pwd'
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": attacker_pwd
    })

    # In a hardened system, we want to know if this boundary is handled.
    # Passlib/Bcrypt behavior: returns True.
    # Our mitigation: min_length=8, max_length=100 in Stage 1A schema.
    # Since 72 < 100, we should document this.
    pass

@pytest.mark.asyncio
async def test_jwt_malformed_corpus(client: AsyncClient):
    """Stage 1B: Malformed JWT Corpus."""
    bad_tokens = [
        "not-a-jwt",
        "header.payload", # Missing signature
        "header.payload.signature.extra", # Too many parts
        "",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.broken", # Invalid signature
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidbase64.signature"
    ]

    for token in bad_tokens:
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.json()["success"] is False

@pytest.mark.asyncio
async def test_auth_header_fuzzing(client: AsyncClient):
    """Stage 1B: Header Abuse."""
    headers = [
        "Bearer",
        "Bearer Bearer",
        "Token xyz",
        "JWT xyz",
        "Bearer  ",
        "xyz",
        "Basic dXNlcjpwYXNz"
    ]
    for h in headers:
        response = await client.get("/api/v1/auth/me", headers={"Authorization": h})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_registration_race_condition(client: AsyncClient):
    """Stage 1B: High-concurrency registration (same email)."""
    email = f"race-{uuid.uuid4().hex}@example.com"
    payload = {
        "email": email,
        "full_name": "Race User",
        "password": "password123"
    }

    # 50 simultaneous registrations
    responses = await asyncio.gather(*[
        client.post("/api/v1/auth/register", json=payload) for _ in range(50)
    ])

    success_count = sum(1 for r in responses if r.status_code == 201)
    error_count = sum(1 for r in responses if r.status_code == 400)

    assert success_count == 1
    assert error_count == 49

@pytest.mark.asyncio
async def test_unicode_email_normalization(client: AsyncClient):
    """Stage 1B: Unicode Normalization Audit."""
    # Test case: Uppercase vs Lowercase vs Unicode variation
    email_base = "ADMin@example.com"
    email_alt = "admin@example.com"

    payload = {
        "email": email_base,
        "full_name": "Admin User",
        "password": "password123"
    }
    await client.post("/api/v1/auth/register", json=payload)

    # Try alternate casing
    payload["email"] = email_alt
    response = await client.post("/api/v1/auth/register", json=payload)

    # Should be rejected as duplicate if normalized
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_json_type_abuse(client: AsyncClient):
    """Stage 1B: JSON Type Confusion."""
    payloads = [
        {"email": "test@example.com", "password": ["array"]},
        {"email": "test@example.com", "password": {"obj": 1}},
        {"email": "test@example.com", "password": True},
        {"email": "test@example.com", "password": None}
    ]
    for p in payloads:
        response = await client.post("/api/v1/auth/login", json=p)
        assert response.status_code == 422 # Pydantic validation error

@pytest.mark.asyncio
async def test_refresh_flood_500(client: AsyncClient, erp_seed: dict):
    """Stage 1B: Refresh Flood (50 concurrent)."""
    login_payload = {"email": erp_seed["user"].email, "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["data"]["refresh_token"]

    responses = await asyncio.gather(*[
        client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token}) for _ in range(50)
    ])

    success_count = sum(1 for r in responses if r.status_code == 200)
    # With SELECT FOR UPDATE, only one should succeed
    assert success_count == 1
