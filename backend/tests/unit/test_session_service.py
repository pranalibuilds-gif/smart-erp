import pytest
import uuid
from datetime import datetime, timedelta, timezone
from app.modules.auth.services.session_service import SessionService
from app.modules.auth.services.auth_service import AuthService
from app.modules.auth.schemas import UserCreate
from app.core.security import decode_token

@pytest.mark.anyio
async def test_create_session(db):
    session_service = SessionService(db)
    user_id = uuid.uuid4()

    tokens = await session_service.create_session(user_id, user_agent="Mozilla")

    assert tokens.access_token is not None
    assert tokens.refresh_token is not None

    payload = decode_token(tokens.refresh_token)
    assert payload["type"] == "refresh"
    assert payload["sub"] == str(user_id)

@pytest.mark.anyio
async def test_refresh_session_rotation(db):
    auth_service = AuthService(db)
    session_service = SessionService(db)

    reg = await auth_service.register_user(UserCreate(
        email="refresh@example.com", password="password", full_name="User"
    ))

    old_refresh = reg.tokens.refresh_token

    # Wait a bit? No need.
    new_tokens = await session_service.refresh_session(old_refresh)

    assert new_tokens.refresh_token != old_refresh
    assert new_tokens.access_token is not None

    # Old token should be unusable (deleted from DB in rotation)
    with pytest.raises(ValueError):
        await session_service.refresh_session(old_refresh)

@pytest.mark.anyio
async def test_revoke_session(db):
    auth_service = AuthService(db)
    session_service = SessionService(db)

    reg = await auth_service.register_user(UserCreate(
        email="logout@example.com", password="password", full_name="User"
    ))

    token = reg.tokens.refresh_token
    await session_service.revoke_session(token)

    # Refresh should fail now
    with pytest.raises(ValueError):
        await session_service.refresh_session(token)

@pytest.mark.anyio
async def test_multi_device_sessions(db):
    auth_service = AuthService(db)
    session_service = SessionService(db)

    reg = await auth_service.register_user(UserCreate(
        email="multi@example.com", password="password", full_name="User"
    ))

    token1 = reg.tokens.refresh_token

    # Second login
    tokens2 = await auth_service.authenticate_user("multi@example.com", "password")
    token2 = tokens2.refresh_token

    assert token1 != token2

    # Both should be valid
    await session_service.refresh_session(token1)
    await session_service.refresh_session(token2)
