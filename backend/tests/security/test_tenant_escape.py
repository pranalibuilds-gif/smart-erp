import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_cross_tenant_ledger_access_denied(client: AsyncClient, multi_company_seed: dict):
    """User in Co B should not see Ledger from Co A, even with valid ID."""
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    ledger_a_id = multi_company_seed["ledger_a"].id

    # Request Ledger A while context is Company B
    response = await client.get(
        f"/api/v1/masters/ledgers/{ledger_a_id}",
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    # Must be 404 (Not Found in this company context)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_tenant_isolation_vouchers(client: AsyncClient, multi_company_seed: dict):
    """Ensure vouchers from another company are not leaked in listing."""
    # Logic: List vouchers for Co B. Should be 0, even though Co A might have some.
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    fy_b_id = multi_company_seed["fy_b"].id

    response = await client.get(
        "/api/v1/vouchers",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Company-ID": str(co_b_id),
            "X-Financial-Year-ID": str(fy_b_id)
        }
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 0
