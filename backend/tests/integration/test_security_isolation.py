import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.modules.auth.models import User, Role, UserCompanyRole
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import Ledger, AccountGroup
from app.core.security import create_access_token, hash_password
from datetime import date


@pytest.fixture
async def multi_tenant_seed(db):
    """Creates two companies and two users."""
    uid = str(uuid.uuid4())[:6]
    def create_user(idx):
        return User(
            email=f"iso-user{idx}-{uid}@example.com",
            hashed_password=hash_password("password"),
            full_name=f"User {idx}",
            is_active=True
        )

    def create_company(idx):
        return Company(name=f"Iso Co {idx}-{uid}", legal_name=f"Co {idx} Ltd", slug=f"iso-co-{idx}-{uid}")

    u1, u2 = create_user(1), create_user(2)
    c1, c2 = create_company(1), create_company(2)
    db.add_all([u1, u2, c1, c2])
    await db.flush()

    # Roles
    res_role = await db.execute(select(Role).where(Role.name == "ADMIN"))
    admin_role = res_role.scalars().first()
    if not admin_role:
        admin_role = Role(name="ADMIN")
        db.add(admin_role)
        await db.flush()

    # Linkage
    db.add(UserCompanyRole(user_id=u1.id, company_id=c1.id, role_id=admin_role.id, is_owner=True))
    db.add(UserCompanyRole(user_id=u2.id, company_id=c2.id, role_id=admin_role.id, is_owner=True))

    # Add some data to C2 that User 1 should NOT see
    g2 = AccountGroup(company_id=c2.id, name="Secret Group", nature="ASSET", is_primary=True)
    db.add(g2)
    await db.flush()
    l2 = Ledger(company_id=c2.id, name="Secret Ledger", group_id=g2.id)
    db.add(l2)

    await db.commit()
    return {
        "u1": u1, "u2": u2,
        "c1": c1, "c2": c2,
        "l2_id": l2.id
    }


@pytest.mark.anyio
async def test_company_isolation_ledger_access(client: AsyncClient, multi_tenant_seed):
    """Verifies that User 1 cannot see or access Ledgers from Company 2."""
    token1 = create_access_token(multi_tenant_seed["u1"].id)

    # Attempt to list ledgers for Company 2 using User 1's token
    headers = {
        "Authorization": f"Bearer {token1}",
        "X-Company-ID": str(multi_tenant_seed["c2"].id)
    }

    # Our dependency get_current_company should fail because User 1 is not in C2
    res = await client.get("/api/v1/masters/ledgers", headers=headers)
    assert res.status_code == 403
    assert "access to this company" in res.json()["message"]


@pytest.mark.anyio
async def test_company_isolation_direct_id_access(client: AsyncClient, multi_tenant_seed):
    """Verifies that User 1 cannot access a specific Ledger ID belonging to Company 2 even if they guess the ID."""
    token1 = create_access_token(multi_tenant_seed["u1"].id)

    # Attempt to access C2's ledger while pretending to be in C1
    headers = {
        "Authorization": f"Bearer {token1}",
        "X-Company-ID": str(multi_tenant_seed["c1"].id)
    }

    l2_id = multi_tenant_seed["l2_id"]
    res = await client.get(f"/api/v1/masters/ledgers/{l2_id}", headers=headers)

    # Should return 404 because the service filters by company_id
    assert res.status_code == 404
