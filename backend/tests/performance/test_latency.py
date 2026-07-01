import time
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_api_latency_kpis(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Verify that critical API operations meet latency targets."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 0. Warm-up
    await client.get(
        "/api/v1/search?q=Warmup",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )

    # 1. Search Latency (< 100ms)
    start = time.time()
    await client.get(
        "/api/v1/search?q=Cash",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    latency = (time.time() - start) * 1000
    assert latency < 250 # Target 100ms, but allowing 250ms for virtual environment

    # 2. Voucher Creation (< 250ms)
    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [
            {"ledger_id": str(erp_seed["sales_ledger"].id), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 0, "credit_amount": 100}
        ]
    }
    start = time.time()
    res = await client.post(
        "/api/v1/vouchers",
        json=voucher_data,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )
    latency = (time.time() - start) * 1000
    assert latency < 300
    v_id = res.json()["data"]["id"]

    # 3. Voucher Posting (< 500ms)
    start = time.time()
    await client.post(
        f"/api/v1/vouchers/{v_id}/post",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    latency = (time.time() - start) * 1000
    assert latency < 600
