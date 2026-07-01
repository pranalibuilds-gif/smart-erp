import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_search_tenant_isolation(client: AsyncClient, multi_company_seed: dict):
    """User searching in Co B should not see results from Co A."""
    token = multi_company_seed["token"]
    co_a_id = multi_company_seed["co_a"].id
    co_b_id = multi_company_seed["co_b"].id
    ledger_a_name = multi_company_seed["ledger_a"].name

    # Search in Co B for "Cash A" (which exists in Co A)
    response = await client.get(
        f"/api/v1/search?q={ledger_a_name}",
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    assert response.status_code == 200
    # Data should be empty because searching in context of Co B
    assert len(response.json()["data"]) == 0
