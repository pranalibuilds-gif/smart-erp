import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import UserCreate, AuthResponse
from app.modules.auth.services.session_service import SessionService
from app.modules.audit.service import AuditService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_service = SessionService(db)
        self.audit_service = AuditService(db)

    async def register_user(
        self,
        user_in: UserCreate,
        user_agent: str | None = None,
        ip_address: str | None = None
    ) -> AuthResponse:
        """
        Registers a new user and automatically logs them in.
        Transactional: User and Session created together.
        """
        # Normalize email
        email_normalized = user_in.email.lower().strip()
        existing_user = await self.user_repo.get_by_email(email_normalized)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

        new_user = User(
            email=email_normalized,
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

        # Log action
        await self.audit_service.log_action(
            user_id=new_user.id,
            company_id=None,
            entity_type="USER",
            entity_id=new_user.id,
            action="REGISTER",
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.db.commit()

        return AuthResponse(
            user=new_user,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type
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
        Uses generic error messages and timing attack resistance.
        """
        # 1. Normalize
        email_normalized = email.lower().strip()

        # 2. Lookup
        user = await self.user_repo.get_by_email(email_normalized)

        # 3. Secure verification (timing resistance)
        # We use a dummy hash if user doesn't exist to ensure bcrypt runs either way
        dummy_hash = "$2b$12$JQ5qK.7e1M4yF/H/nN.rkeH5.XzXp/7QZ/XW/e1.r.e.r.e.r.e.r."
        stored_hash = user.hashed_password if user else dummy_hash

        is_valid = verify_password(password, stored_hash)

        if not user or not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="User account is inactive"
            )

        tokens = await self.session_service.create_session(
            user.id, user_agent, ip_address
        )

        # Log action
        await self.audit_service.log_action(
            user_id=user.id,
            company_id=None,
            entity_type="USER",
            entity_id=user.id,
            action="LOGIN",
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.db.commit()

        return tokens
