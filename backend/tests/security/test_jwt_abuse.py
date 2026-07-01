import pytest
from httpx import AsyncClient
from app.core.security import create_refresh_token, create_access_token
import uuid

@pytest.mark.asyncio
async def test_refresh_token_used_as_access_denied(client: AsyncClient, erp_seed: dict):
    """A refresh token should not be accepted as a Bearer access token."""
    user_id = erp_seed["user"].id
    refresh_token = create_refresh_token(subject=user_id)

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    # The get_current_user dependency checks for type="access"
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_access_token_used_as_refresh_denied(client: AsyncClient, erp_seed: dict):
    """An access token should not be accepted in the refresh endpoint."""
    user_id = erp_seed["user"].id
    access_token = create_access_token(subject=user_id)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token}
    )
    # The session service checks for type="refresh"
    assert response.status_code == 401
