import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_token,
    decode_token
)
from app.core.config import settings
from app.modules.auth.repository import RefreshTokenRepository
from app.modules.auth.models import RefreshToken
from app.modules.auth.schemas import Token


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RefreshTokenRepository(db)

    async def create_session(
        self,
        user_id: uuid.UUID,
        user_agent: str | None = None,
        ip_address: str | None = None
    ) -> Token:
        """
        Creates a new session for a user.
        Generates access and refresh tokens and stores the hashed refresh token.
        """
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        # Calculate expiry
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )

        await self.repo.create(new_refresh_token)
        # We don\u0027t commit here to support transactional registration if needed

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_session(
        self,
        refresh_token: str,
        user_agent: str | None = None,
        ip_address: str | None = None
    ) -> Token:
        """
        Implements Refresh Token Rotation.
        Validates the token, revokes the old one, and issues a new pair.
        """
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")

            user_id = uuid.UUID(payload.get("sub"))
        except (JWTError, ValueError):
            raise ValueError("Invalid or expired refresh token")

        token_hash = hash_token(refresh_token)
        stored_token = await self.repo.get_by_hash(token_hash, for_update=True)

        if not stored_token or stored_token.expires_at < datetime.now(timezone.utc):
            if stored_token:
                await self.repo.delete(stored_token.id)
            raise ValueError("Refresh token expired or invalid")

        # Rotation: Delete old token and create new session
        await self.repo.delete(stored_token.id)

        return await self.create_session(user_id, user_agent, ip_address)

    async def revoke_session(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)
        stored_token = await self.repo.get_by_hash(token_hash, for_update=True)
        if stored_token:
            await self.repo.revoke(stored_token.id)
            await self.db.commit()

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        await self.repo.revoke_all_for_user(user_id)
        await self.db.commit()
