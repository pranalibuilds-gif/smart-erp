import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.models import User
from app.modules.companies.models import Company

@pytest.mark.asyncio
async def test_cross_tenant_contextual_rbac(client: AsyncClient, contextual_rbac_seed: dict):
    """
    Attack: User is ADMIN in Company A and VIEWER in Company B.
    Verify they CANNOT perform ADMIN actions in Company B context.
    """
    token = contextual_rbac_seed["token"]
    co_b_id = contextual_rbac_seed["co_b"].id

    # Attempt an Admin-only action (Update Company) using Company B ID
    # in the header context.
    payload = {"name": "Hacked Name"}
    response = await client.put(
        f"/api/v1/companies/{co_b_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    # Should be 403 Forbidden because in Co B they are only a VIEWER
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_idor_cross_company_resource_leak(client: AsyncClient, multi_company_seed: dict):
    """
    Attack: Authenticated in Co B, but request a specific UUID from Co A.
    Verify 404 (or 403) to prevent data leaking.
    """
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    ledger_a_id = multi_company_seed["ledger_a"].id # Exists in Co A

    # Request Ledger A with Co B context
    response = await client.get(
        f"/api/v1/masters/ledgers/{ledger_a_id}",
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    # Expected 404: The ledger is not visible in Co B's scope
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_header_bypass_missing_company_id(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """Attack: Omit X-Company-ID header."""
    response = await client.get(
        "/api/v1/masters/ledgers",
        headers={"Authorization": f"Bearer {accountant_token}"}
    )
    # FastAPI should return 422 Unprocessable Entity for missing required header
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_header_bypass_manipulated_id(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """Attack: Use a valid UUID that the user doesn't belong to."""
    random_company_id = uuid.uuid4()
    response = await client.get(
        "/api/v1/masters/ledgers",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(random_company_id)}
    )
    # Should be 403 Forbidden (Membership check fails) or 400 (Invalid ID)
    assert response.status_code in [403, 400]

@pytest.mark.asyncio
async def test_horizontal_escalation_user_profile(client: AsyncClient, multi_company_seed: dict):
    """
    Attack: User A attempts to view/modify User B's profile.
    (Note: ERP doesn't have a /users/{id} endpoint yet, but /auth/me is personal)
    """
    pass

@pytest.mark.asyncio
async def test_permission_string_fuzzing(client: AsyncClient, erp_seed: dict, viewer_token: str):
    """
    Attack: Viewer attempts to access endpoints by guessing or fuzzing.
    We'll test a few high-value targets.
    """
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    targets = [
        ("POST", "/api/v1/vouchers"),
        ("POST", "/api/v1/billing/invoices"),
        ("PATCH", f"/api/v1/masters/ledgers/{uuid.uuid4()}"), # Changed DELETE to PATCH (exists)
        ("POST", f"/api/v1/companies/{company_id}/invite"),
    ]

    for method, path in targets:
        response = await client.request(
            method, path,
            headers={"Authorization": f"Bearer {viewer_token}", "X-Company-ID": str(company_id)}
        )
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_superuser_bypass_verified(client: AsyncClient, superuser_token: str, erp_seed: dict):
    """Verification: Superuser should bypass all RBAC checks."""
    company_id = erp_seed["company"].id

    # Superuser listing ledgers in a company they aren't explicitly a 'member' of
    # (Assuming the seed setup didn't add them as member)
    response = await client.get(
        "/api/v1/masters/ledgers",
        headers={"Authorization": f"Bearer {superuser_token}", "X-Company-ID": str(company_id)}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_scope_mismatch_vulnerability(client: AsyncClient, contextual_rbac_seed: dict):
    """
    Attack: Authenticated as ADMIN in Co A.
    Attempt to update Co B (where I might not even be a member)
    by providing Co A ID in the header but Co B ID in the path.
    """
    token = contextual_rbac_seed["token"]
    co_a_id = contextual_rbac_seed["co_a"].id
    co_b_id = contextual_rbac_seed["co_b"].id

    # Header claims Co A (I am ADMIN there)
    # Path targets Co B
    payload = {"name": "Vulnerability Test"}
    response = await client.put(
        f"/api/v1/companies/{co_b_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_a_id)}
    )

    # This SHOULD be 403 or 400 because the authorized context (Co A)
    # does not match the resource being modified (Co B).
    # If it returns 200, we have a scope mismatch leak.
    assert response.status_code != 200
