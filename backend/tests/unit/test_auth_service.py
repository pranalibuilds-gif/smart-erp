import pytest
from fastapi import HTTPException
from app.modules.auth.services.auth_service import AuthService
from app.modules.auth.schemas import UserCreate
from app.core.security import verify_password

@pytest.mark.anyio
async def test_register_user_success(db):
    auth_service = AuthService(db)
    user_in = UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )

    response = await auth_service.register_user(user_in)

    assert response.user.email == "test@example.com"
    assert response.user.full_name == "Test User"
    assert response.access_token is not None
    assert response.refresh_token is not None

@pytest.mark.anyio
async def test_register_user_duplicate_email(db):
    auth_service = AuthService(db)
    user_in = UserCreate(
        email="dup@example.com",
        password="password123",
        full_name="Test User"
    )

    await auth_service.register_user(user_in)

    with pytest.raises(HTTPException) as exc:
        await auth_service.register_user(user_in)
    assert exc.value.status_code == 400

@pytest.mark.anyio
async def test_authenticate_user_success(db):
    auth_service = AuthService(db)
    email = "login@example.com"
    password = "password123"

    await auth_service.register_user(UserCreate(
        email=email, password=password, full_name="Login User"
    ))

    tokens = await auth_service.authenticate_user(email, password)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None

@pytest.mark.anyio
async def test_authenticate_user_invalid_credentials(db):
    auth_service = AuthService(db)

    # Non-existent user
    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate_user("none@example.com", "pass")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Incorrect email or password"

    # Wrong password
    await auth_service.register_user(UserCreate(
        email="wrong@example.com", password="correctpassword", full_name="User"
    ))
    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate_user("wrong@example.com", "wrongpassword")
    assert exc.value.status_code == 401
