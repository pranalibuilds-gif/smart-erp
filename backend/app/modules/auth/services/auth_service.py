import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import UserCreate, UserRegistrationResponse
from app.modules.auth.services.session_service import SessionService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_service = SessionService(db)

    async def register_user(
        self,
        user_in: UserCreate,
        user_agent: str | None = None,
        ip_address: str | None = None
    ) -> UserRegistrationResponse:
        """
        Registers a new user and automatically logs them in.
        Transactional: User and Session created together.
        """
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

        new_user = User(
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            full_name=user_in.full_name,
            is_active=True
        )

        await self.user_repo.create(new_user)
        await self.db.flush() # Populate ID

        # Create initial session
        tokens = await self.session_service.create_session(
            new_user.id, user_agent, ip_address
        )

        await self.db.commit()
        await self.db.refresh(new_user)

        return UserRegistrationResponse(
            user=new_user,
            tokens=tokens
        )

    async def authenticate_user(
        self,
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None
    ):
        """
        Validates credentials and returns a new session.
        Uses generic error messages to prevent enumeration.
        """
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )

        tokens = await self.session_service.create_session(
            user.id, user_agent, ip_address
        )
        await self.db.commit()

        return tokens
