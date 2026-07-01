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
from sqlalchemy import select
from app.core.security import hash_password, create_access_token

# IMPORTANT: Import all models
from app.modules.auth.models import User, Role, Permission, RolePermission, UserCompanyRole, RefreshToken
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import AccountGroup, Ledger, StockItem, Unit, Warehouse
from app.modules.parties.models import Party


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

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
    transport = ASGITransport(app=app, raise_app_exceptions=False)
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
    cap_ledger = Ledger(company_id=company.id, group_id=liabilities.id, name="Capital")
    inv_ledger = Ledger(company_id=company.id, group_id=curr_assets.id, name="Inventory")
    gain_ledger = Ledger(company_id=company.id, group_id=income.id, name="Inventory Adjustment Gain")
    loss_ledger = Ledger(company_id=company.id, group_id=expenses.id, name="Inventory Adjustment Loss")
    db.add_all([sales_ledger, pur_ledger, cap_ledger, inv_ledger, gain_ledger, loss_ledger])

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
    from app.shared.constants.permissions import ALL_PERMISSIONS
    all_perms = []
    for p_name in ALL_PERMISSIONS:
        res = await db.execute(select(Permission).where(Permission.name == p_name))
        perm = res.scalar_one_or_none()
        if not perm:
            perm = Permission(name=p_name)
            db.add(perm)
            await db.flush()
        all_perms.append(perm)

    role = Role(name=f"Admin-{uid}", permissions=all_perms)
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
        "pur_ledger": pur_ledger,
        "cap_ledger": cap_ledger,
        "inv_ledger": inv_ledger,
        "gain_ledger": gain_ledger,
        "loss_ledger": loss_ledger
    }

from sqlalchemy.orm import selectinload

# ... previous imports ...

@pytest.fixture
def admin_token(erp_seed):
    return create_access_token(subject=erp_seed["user"].id)

@pytest.fixture
async def accountant_token(db, erp_seed):
    """Fixture to provide a token for a user with accountant permissions."""
    uid = str(uuid.uuid4())[:8]
    user = User(
        email=f"accountant-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="Accountant User",
        is_active=True
    )
    db.add(user)

    # Accountant Role
    role = Role(name=f"Accountant-{uid}")
    db.add(role)
    await db.flush()

    # Assign permissions
    perms = [
        "voucher:create", "voucher:view", "voucher:post", "voucher:cancel",
        "invoice:create", "invoice:view", "invoice:post", "invoice:cancel",
        "report:view", "audit:view", "search:use",
        "banking:transact", "banking:view",
        "company:manage", "company:view",
        "masters:view", "masters:manage",
        "inventory:view", "inventory:manage"
    ]
    for p_name in perms:
        res = await db.execute(select(Permission).where(Permission.name == p_name))
        perm = res.scalar_one_or_none()
        if not perm:
            perm = Permission(name=p_name)
            db.add(perm)
            await db.flush()

        # Load permissions eagerly to avoid lazy load issue
        stmt = select(Role).where(Role.id == role.id).options(selectinload(Role.permissions))
        role_res = await db.execute(stmt)
        role_obj = role_res.scalar_one()
        if perm not in role_obj.permissions:
            role_obj.permissions.append(perm)

    db.add(UserCompanyRole(user_id=user.id, company_id=erp_seed["company"].id, role_id=role.id))
    await db.commit()
    return create_access_token(subject=user.id)

@pytest.fixture
async def viewer_token(db, erp_seed):
    """Fixture to provide a token for a user with read-only permissions."""
    uid = str(uuid.uuid4())[:8]
    user = User(
        email=f"viewer-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="Viewer User",
        is_active=True
    )
    db.add(user)

    # Viewer Role
    role = Role(name=f"Viewer-{uid}")
    db.add(role)
    await db.flush()

    # Assign permissions
    perms = ["voucher:view", "invoice:view", "report:view", "masters:view"]
    for p_name in perms:
        res = await db.execute(select(Permission).where(Permission.name == p_name))
        perm = res.scalar_one_or_none()
        if not perm:
            perm = Permission(name=p_name)
            db.add(perm)
            await db.flush()

        stmt = select(Role).where(Role.id == role.id).options(selectinload(Role.permissions))
        role_res = await db.execute(stmt)
        role_obj = role_res.scalar_one()
        if perm not in role_obj.permissions:
            role_obj.permissions.append(perm)

    db.add(UserCompanyRole(user_id=user.id, company_id=erp_seed["company"].id, role_id=role.id))
    await db.commit()
    return create_access_token(subject=user.id)

@pytest.fixture
async def multi_company_seed(db):
    """Seed data for 2 companies with a shared user."""
    uid = str(uuid.uuid4())[:8]

    # Shared User
    user = User(
        email=f"shared-user-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="Shared User",
        is_active=True
    )
    db.add(user)
    await db.flush()

    # Company A
    co_a = Company(name=f"Co A {uid}", legal_name=f"Co A {uid} Ltd", slug=f"co-a-{uid}")
    db.add(co_a)
    # Company B
    co_b = Company(name=f"Co B {uid}", legal_name=f"Co B {uid} Ltd", slug=f"co-b-{uid}")
    db.add(co_b)
    await db.flush()

    # Assign permissions to Admin
    from app.shared.constants.permissions import ALL_PERMISSIONS
    all_perms = []
    for p_name in ALL_PERMISSIONS:
        res = await db.execute(select(Permission).where(Permission.name == p_name))
        perm = res.scalar_one_or_none()
        if not perm:
            perm = Permission(name=p_name)
            db.add(perm)
            await db.flush()
        all_perms.append(perm)

    # Roles
    admin_role = Role(name=f"Admin-{uid}", permissions=all_perms)
    db.add(admin_role)
    await db.flush()

    # User in both companies
    db.add(UserCompanyRole(user_id=user.id, company_id=co_a.id, role_id=admin_role.id, is_owner=True))
    db.add(UserCompanyRole(user_id=user.id, company_id=co_b.id, role_id=admin_role.id, is_owner=True))

    await db.flush()

    # Financial Years
    fy_a = FinancialYear(company_id=co_a.id, name="25-26", start_date=date(2025, 4, 1), end_date=date(2026, 3, 31))
    fy_b = FinancialYear(company_id=co_b.id, name="25-26", start_date=date(2025, 4, 1), end_date=date(2026, 3, 31))
    db.add_all([fy_a, fy_b])

    # Ledger in Co A
    grp_a = AccountGroup(company_id=co_a.id, name="Assets", nature="ASSET", is_primary=True)
    db.add(grp_a)
    await db.flush()
    ledger_a = Ledger(company_id=co_a.id, group_id=grp_a.id, name="Cash A")
    db.add(ledger_a)
    await db.flush()

    # Party in Co A
    party_a = Party(company_id=co_a.id, ledger_id=ledger_a.id, name="Client A", is_customer=True)
    db.add(party_a)

    # Warehouse in Co A
    wh_a = Warehouse(company_id=co_a.id, name="WH A", code="WHA")
    db.add(wh_a)

    # Stock Item in Co A
    unit_a = Unit(company_id=co_a.id, name="PCS")
    db.add(unit_a)
    await db.flush()
    item_a = StockItem(company_id=co_a.id, unit_id=unit_a.id, name="Item A", current_quantity=0, average_cost=0)
    db.add(item_a)

    # Warehouse in Co B
    wh_b = Warehouse(company_id=co_b.id, name="WH B", code="WHB")
    db.add(wh_b)

    # Ledger in Co B
    grp_b = AccountGroup(company_id=co_b.id, name="Assets B", nature="ASSET", is_primary=True)
    db.add(grp_b)
    await db.flush()
    ledger_b = Ledger(company_id=co_b.id, group_id=grp_b.id, name="Cash B")
    db.add(ledger_b)

    await db.commit()

    return {
        "user": user,
        "co_a": co_a,
        "co_b": co_b,
        "fy_a": fy_a,
        "fy_b": fy_b,
        "ledger_a": ledger_a,
        "ledger_b": ledger_b,
        "party_a": party_a,
        "wh_a": wh_a,
        "wh_b": wh_b,
        "item_a": item_a,
        "token": create_access_token(subject=user.id)
    }

@pytest.fixture
def company_id(erp_seed):
    return erp_seed["company"].id

@pytest.fixture
async def superuser_token(db):
    """Fixture for a global superuser."""
    uid = str(uuid.uuid4())[:8]
    user = User(
        email=f"root-{uid}@smaterp.internal",
        hashed_password=hash_password("password123"),
        full_name="Root Admin",
        is_active=True,
        is_superuser=True
    )
    db.add(user)
    await db.commit()
    return create_access_token(subject=user.id)

@pytest.fixture
async def contextual_rbac_seed(db):
    """User is Admin in Co A and Viewer in Co B."""
    uid = str(uuid.uuid4())[:8]
    user = User(email=f"rbac-{uid}@example.com", hashed_password=hash_password("password123"), full_name="RBAC User", is_active=True)
    db.add(user)
    await db.flush()

    co_a = Company(name=f"Co A {uid}", legal_name=f"Co A {uid} Ltd", slug=f"co-a-{uid}")
    co_b = Company(name=f"Co B {uid}", legal_name=f"Co B {uid} Ltd", slug=f"co-b-{uid}")
    db.add_all([co_a, co_b])
    await db.flush()

    # Permissions
    from app.shared.constants.permissions import ALL_PERMISSIONS
    all_perms = []
    for p_name in ALL_PERMISSIONS:
        res = await db.execute(select(Permission).where(Permission.name == p_name))
        perm = res.scalar_one_or_none()
        if not perm:
            perm = Permission(name=p_name)
            db.add(perm)
            await db.flush()
        all_perms.append(perm)

    # Admin Role for Co A
    admin_role = Role(name=f"Admin-{uid}", permissions=all_perms)
    # Viewer Role for Co B
    view_perms = [p for p in all_perms if p.name in ["company:view", "report:view", "masters:view"]]
    viewer_role = Role(name=f"Viewer-{uid}", permissions=view_perms)
    db.add_all([admin_role, viewer_role])
    await db.flush()

    db.add(UserCompanyRole(user_id=user.id, company_id=co_a.id, role_id=admin_role.id))
    db.add(UserCompanyRole(user_id=user.id, company_id=co_b.id, role_id=viewer_role.id))

    await db.commit()
    return {
        "user": user,
        "co_a": co_a,
        "co_b": co_b,
        "token": create_access_token(subject=user.id)
    }
