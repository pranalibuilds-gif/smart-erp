import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.shared.database.base import Base
from app.core.config import settings

# IMPORTANT: Import all models here so they are registered with Base.metadata
from app.modules.auth.models import User, Role, Permission, RolePermission, UserCompanyRole, RefreshToken
from app.modules.companies.models import Company

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def test_engine():
    """Create a separate engine for each test to avoid loop issues on Windows."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        future=True,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session for tests."""
    Session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with Session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Reusable async test client.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
