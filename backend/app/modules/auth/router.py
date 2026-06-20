from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse
from app.modules.auth.schemas import (
    UserCreate,
    LoginRequest,
    RefreshRequest,
    AuthResponse,
    Token,
    UserRead
)
from app.modules.auth.services.auth_service import AuthService
from app.modules.auth.services.session_service import SessionService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=SuccessResponse[AuthResponse], status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user and returns access and refresh tokens.
    """
    auth_service = AuthService(db)
    result = await auth_service.register_user(
        user_in,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    return SuccessResponse(data=result)

@router.post("/login", response_model=SuccessResponse[AuthResponse])
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and returns access and refresh tokens.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.authenticate_user(
        login_data.email,
        login_data.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )

    # We need to fetch the user to return AuthResponse
    # Alternatively, AuthService.authenticate_user could return AuthResponse
    user = await auth_service.user_repo.get_by_email(login_data.email)

    return SuccessResponse(data=AuthResponse(
        user=user,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type
    ))

@router.post("/refresh", response_model=SuccessResponse[Token])
async def refresh(
    request: Request,
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Rotates the refresh token and returns a new token pair.
    """
    session_service = SessionService(db)
    try:
        new_tokens = await session_service.refresh_session(
            refresh_data.refresh_token,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None
        )
        await db.commit()
        return SuccessResponse(data=new_tokens)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout", response_model=SuccessResponse[None])
async def logout(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Revokes the provided refresh token.
    """
    session_service = SessionService(db)
    await session_service.revoke_session(refresh_data.refresh_token)
    return SuccessResponse(data=None, message="Logged out successfully")

@router.post("/logout-all", response_model=SuccessResponse[None])
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revokes all active sessions for the current user.
    """
    session_service = SessionService(db)
    await session_service.revoke_all_sessions(current_user.id)
    return SuccessResponse(data=None, message="All sessions revoked")

@router.get("/me", response_model=SuccessResponse[UserRead])
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the current user profile.
    """
    return SuccessResponse(data=current_user)
