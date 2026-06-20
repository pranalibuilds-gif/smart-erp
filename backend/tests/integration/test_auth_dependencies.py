import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.models import User, Role, Permission, UserCompanyRole
from app.modules.companies.models import Company
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.main import app
from fastapi import APIRouter, Depends
from app.modules.auth.dependencies import get_current_user, get_current_company, PermissionRequired
from app.shared.schemas.responses import SuccessResponse

# Rename to avoid pytest collection
auth_test_router = APIRouter(prefix="/auth-test-deps")

@auth_test_router.get("/user", response_model=SuccessResponse[dict])
async def endpoint_test_user(user: User = Depends(get_current_user)):
    return SuccessResponse(data={"email": user.email})

@auth_test_router.get("/company", response_model=SuccessResponse[dict])
async def endpoint_test_company(company: Company = Depends(get_current_company)):
    return SuccessResponse(data={"name": company.name})

@auth_test_router.get("/permission", dependencies=[Depends(PermissionRequired("test:view"))])
async def endpoint_test_permission():
    return SuccessResponse(data={"allowed": True})

# Mount the router for tests
app.include_router(auth_test_router)

@pytest.fixture
async def seed_data(db):
    uid = str(uuid.uuid4())[:8]
    # 1. Create User
    user = User(
        email=f"dep-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="Dep User",
        is_active=True
    )
    db.add(user)

    # 2. Create Company
    company = Company(name="Test Co", slug=f"test-co-{uid}")
    db.add(company)

    # 3. Create Superuser
    superuser = User(
        email=f"super-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="Super User",
        is_superuser=True
    )
    db.add(superuser)

    # 4. Create Role & Permission
    # Use unique name per test to avoid collision, or catch error
    perm_name = f"test:view-{uid}"
    permission = Permission(name=perm_name)
    db.add(permission)

    # Update router dependency for THIS test? No, easier to just seed "test:view" once per session.
    # Actually let\u0027s just use the hardcoded one but only add if missing.
    from sqlalchemy import select
    res = await db.execute(select(Permission).where(Permission.name == "test:view"))
    p_fixed = res.scalars().first()
    if not p_fixed:
        p_fixed = Permission(name="test:view")
        db.add(p_fixed)

    role = Role(name=f"Role-{uid}")
    role.permissions.append(p_fixed)
    db.add(role)

    await db.flush()

    # 5. Assign User to Company
    ucr = UserCompanyRole(user_id=user.id, company_id=company.id, role_id=role.id)
    db.add(ucr)

    await db.commit()
    return {
        "user": user,
        "company": company,
        "superuser": superuser,
        "role": role,
        "permission": p_fixed
    }

@pytest.mark.anyio
async def test_get_current_user_success(client: AsyncClient, seed_data):
    token = create_access_token(seed_data["user"].id)
    response = await client.get("/auth-test-deps/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["data"]["email"].startswith("dep-")

@pytest.mark.anyio
async def test_get_current_user_invalid_type(client: AsyncClient, seed_data):
    token = create_refresh_token(seed_data["user"].id)
    response = await client.get("/auth-test-deps/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

@pytest.mark.anyio
async def test_get_current_company_success(client: AsyncClient, seed_data):
    token = create_access_token(seed_data["user"].id)
    response = await client.get(
        "/auth-test-deps/company",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Company-ID": str(seed_data["company"].id)
        }
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Test Co"

@pytest.mark.anyio
async def test_get_current_company_no_access(client: AsyncClient, seed_data, db):
    other_company = Company(name="Other", slug=f"other-{uuid.uuid4()}")
    db.add(other_company)
    await db.commit()

    token = create_access_token(seed_data["user"].id)
    response = await client.get(
        "/auth-test-deps/company",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Company-ID": str(other_company.id)
        }
    )
    assert response.status_code == 403

@pytest.mark.anyio
async def test_permission_required_granted(client: AsyncClient, seed_data):
    token = create_access_token(seed_data["user"].id)
    response = await client.get(
        "/auth-test-deps/permission",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Company-ID": str(seed_data["company"].id)
        }
    )
    assert response.status_code == 200

@pytest.mark.anyio
async def test_superuser_bypass(client: AsyncClient, seed_data):
    token = create_access_token(seed_data["superuser"].id)
    response = await client.get(
        "/auth-test-deps/permission",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Company-ID": str(seed_data["company"].id)
        }
    )
    assert response.status_code == 200
