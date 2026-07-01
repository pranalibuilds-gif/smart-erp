import pytest
from httpx import AsyncClient
from app.core.security import create_refresh_token, create_access_token
import uuid

@pytest.mark.asyncio
async def test_refresh_token_rotation_and_replay_denied(client: AsyncClient, erp_seed: dict):
    """Reuse of a refresh token after rotation should fail."""
    user = erp_seed["user"]

    # 1. Login to get first refresh token
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"}
    )
    tokens = response.json()["data"]
    rt1 = tokens["refresh_token"]

    # 2. Refresh once to get rt2
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": rt1}
    )
    assert response.status_code == 200
    rt2 = response.json()["data"]["refresh_token"]

    # 3. Attempt to use rt1 again (Replay Attack)
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": rt1}
    )
    # Rotation logic should revoke rt1 or detect reuse
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client: AsyncClient, erp_seed: dict):
    """After logout, the refresh token should be invalid."""
    user = erp_seed["user"]

    # 1. Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"}
    )
    rt = response.json()["data"]["refresh_token"]

    # 2. Logout
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": rt}
    )
    assert response.status_code == 200

    # 3. Try to use it again
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": rt}
    )
    assert response.status_code == 401
