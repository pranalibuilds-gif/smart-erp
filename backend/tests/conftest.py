import pytest
import asyncio
import uuid
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import date

from app.main import app
from app.shared.database.base import Base
from app.shared.database.session import get_db
from app.core.config import settings
from app.core.security import hash_password

# IMPORTANT: Import all models
from app.modules.auth.models import User, Role, Permission, RolePermission, UserCompanyRole, RefreshToken
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import AccountGroup, Ledger, StockItem, Unit, Warehouse
from app.modules.parties.models import Party


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

    # Dependency override that provides a NEW session per request
    async def _get_db_override():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override

    async with async_session() as session:
        yield session

    app.dependency_overrides.clear()

@pytest.fixture
async def client(db) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def erp_seed(db):
    uid = str(uuid.uuid4())[:8]
    company = Company(name=f"ERP Co {uid}", legal_name="ERP Ltd", slug=f"erp-co-{uid}")
    db.add(company)

    user = User(
        email=f"erp-user-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="ERP User",
        is_active=True
    )
    db.add(user)
    await db.flush()

    fy = FinancialYear(
        company_id=company.id,
        name="2025-2026",
        start_date=date(2025, 4, 1),
        end_date=date(2026, 3, 31)
    )
    db.add(fy)

    # Required Groups
    assets = AccountGroup(company_id=company.id, name="Assets", nature="ASSET", is_primary=True)
    income = AccountGroup(company_id=company.id, name="Income", nature="INCOME", is_primary=True)
    expenses = AccountGroup(company_id=company.id, name="Expenses", nature="EXPENSE", is_primary=True)
    liabilities = AccountGroup(company_id=company.id, name="Liabilities", nature="LIABILITY", is_primary=True)
    db.add_all([assets, income, expenses, liabilities])
    await db.flush()

    # Subgroups
    curr_assets = AccountGroup(company_id=company.id, name="Current Assets", parent_id=assets.id)
    debtors = AccountGroup(company_id=company.id, name="Sundry Debtors", parent_id=curr_assets.id)
    creditors = AccountGroup(company_id=company.id, name="Sundry Creditors", parent_id=liabilities.id)
    db.add_all([curr_assets, debtors, creditors])
    await db.flush()

    # Required Ledgers
    sales_ledger = Ledger(company_id=company.id, group_id=income.id, name="Sales")
    pur_ledger = Ledger(company_id=company.id, group_id=expenses.id, name="Purchase")
    db.add_all([sales_ledger, pur_ledger])

    # Inventory items
    unit = Unit(company_id=company.id, name="PCS")
    db.add(unit)
    await db.flush()

    item = StockItem(company_id=company.id, unit_id=unit.id, name="Widget", current_quantity=0, average_cost=0)
    db.add(item)

    # Warehouse
    warehouse = Warehouse(company_id=company.id, name="Main", code="MAIN")
    db.add(warehouse)
    await db.flush()

    # Party
    p_ledger = Ledger(company_id=company.id, group_id=debtors.id, name="Test Client")
    db.add(p_ledger)
    await db.flush()
    party = Party(company_id=company.id, ledger_id=p_ledger.id, name="Test Client", is_customer=True)
    db.add(party)

    # Role
    role = Role(name=f"Admin-{uid}")
    db.add(role)
    await db.flush()
    db.add(UserCompanyRole(user_id=user.id, company_id=company.id, role_id=role.id, is_owner=True))

    await db.commit()
    return {
        "user": user,
        "company": company,
        "fy": fy,
        "party": party,
        "item": item,
        "warehouse": warehouse,
        "sales_ledger": sales_ledger,
        "pur_ledger": pur_ledger
    }
