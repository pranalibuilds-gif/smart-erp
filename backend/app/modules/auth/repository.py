import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.models import User, RefreshToken


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        # We don\u0027t commit here to allow transactional registration in service
        return user


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.db.add(refresh_token)
        return refresh_token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at == None
            )
        )
        return result.scalars().first()

    async def revoke(self, token_id: uuid.UUID) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def delete_expired(self) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(timezone.utc))
        )

    async def delete(self, token_id: uuid.UUID) -> None:
        await self.db.execute(delete(RefreshToken).where(RefreshToken.id == token_id))
