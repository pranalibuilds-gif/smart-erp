import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_voucher_post_idempotency(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Posting an already posted voucher should return an error, not double-post balances."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 1. Create and Post
    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [
            {"ledger_id": str(erp_seed["sales_ledger"].id), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 0, "credit_amount": 100}
        ]
    }
    res = await client.post("/api/v1/vouchers", json=voucher_data, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    v_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/vouchers/{v_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # 2. Attempt Second Post (Sequential Retry)
    response = await client.post(
        f"/api/v1/vouchers/{v_id}/post",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    # Should fail as already posted
    assert response.status_code == 400
    assert "cannot post" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_fy_close_idempotency(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Closing an already closed FY should return 400."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 1. Close once
    await client.post(f"/api/v1/companies/{company_id}/financial-years/{fy_id}/close", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # 2. Close again
    response = await client.post(f"/api/v1/companies/{company_id}/financial-years/{fy_id}/close", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    assert response.status_code == 400
    assert "already closed" in response.json()["message"].lower()
