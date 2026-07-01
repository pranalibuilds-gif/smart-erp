import asyncio
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_ledger_lock_ordering_prevents_deadlock(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Stress test ledger locking with conflicting order to ensure no deadlocks occur."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    l1 = erp_seed["sales_ledger"].id
    l2 = erp_seed["pur_ledger"].id

    # Sort them to know which is lower to intentionally reverse the order in payload
    ids = sorted([l1, l2])
    low_id, high_id = ids[0], ids[1]

    async def create_and_post_voucher(entries):
        voucher_data = {
            "voucher_type": "JOURNAL",
            "voucher_date": "2024-06-01",
            "entries": entries
        }
        res = await client.post(
            "/api/v1/vouchers",
            json=voucher_data,
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
        )
        v_id = res.json()["data"]["id"]
        return await client.post(
            f"/api/v1/vouchers/{v_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )

    # Payload 1: low_id first
    entries1 = [
        {"ledger_id": str(low_id), "debit_amount": 100, "credit_amount": 0},
        {"ledger_id": str(high_id), "debit_amount": 0, "credit_amount": 100}
    ]
    # Payload 2: high_id first
    entries2 = [
        {"ledger_id": str(high_id), "debit_amount": 100, "credit_amount": 0},
        {"ledger_id": str(low_id), "debit_amount": 0, "credit_amount": 100}
    ]

    # Run many pairs
    tasks = []
    for _ in range(10):
        tasks.append(create_and_post_voucher(entries1))
        tasks.append(create_and_post_voucher(entries2))

    responses = await asyncio.gather(*tasks)

    # All should succeed if locking order is normalized by service
    for r in responses:
        assert r.status_code == 200
