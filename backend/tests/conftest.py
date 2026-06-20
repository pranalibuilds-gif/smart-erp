import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.main import app
from app.shared.database.base import Base
from app.shared.database.session import get_db
from app.core.config import settings

# IMPORTANT: Import all models
from app.modules.auth.models import User, Role, Permission, RolePermission, UserCompanyRole, RefreshToken
from app.modules.companies.models import Company

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def _engine():
    # Use NullPool to avoid loop issues with pooled connections on Windows
    engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db(_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        app.dependency_overrides[get_db] = lambda: session
        yield session
        app.dependency_overrides.clear()

@pytest.fixture
async def client(db) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
