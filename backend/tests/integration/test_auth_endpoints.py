import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.anyio
async def test_auth_flow(client: AsyncClient):
    uid = str(uuid.uuid4())[:8]
    email = f"user-{uid}@example.com"
    password = "password123"

    # 1. Register
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": password
        }
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()["data"]
    assert reg_data["user"]["email"] == email

    access_token = reg_data["access_token"]
    refresh_token = reg_data["refresh_token"]

    # 2. Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()["data"]
    assert login_data["access_token"] != access_token

    # 3. Get Me
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["data"]["email"] == email

    # 4. Refresh
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()["data"]
    assert new_tokens["access_token"] != access_token
    assert new_tokens["refresh_token"] != refresh_token

    # 5. Logout
    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert logout_response.status_code == 200

    # 6. Verify revoked
    re_refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert re_refresh.status_code == 401
