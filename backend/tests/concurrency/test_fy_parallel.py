import asyncio
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_fy_close_vs_voucher_post_race(client: AsyncClient, admin_token: str, accountant_token: str, erp_seed: dict):
    """Ensure no voucher is posted into an FY if it's being closed simultaneously."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 1. Create a draft voucher
    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [
            {"ledger_id": str(erp_seed["sales_ledger"].id), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 0, "credit_amount": 100}
        ]
    }
    res = await client.post(
        "/api/v1/vouchers",
        json=voucher_data,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )
    v_id = res.json()["data"]["id"]

    # 2. Parallel Close FY and Post Voucher
    async def close_fy():
        return await client.post(
            f"/api/v1/companies/{company_id}/financial-years/{fy_id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "X-Company-ID": str(company_id)}
        )

    async def post_voucher():
        return await client.post(
            f"/api/v1/vouchers/{v_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )

    # Use a small delay or just pure parallel gather
    # We want to see if post succeeds AFTER close or if close blocks post
    # In Postgres, both use locks, so one will wait for other.
    responses = await asyncio.gather(close_fy(), post_voucher())

    # If Close happens first, Post should fail with "Financial Year is closed"
    # If Post happens first, Close should succeed (but FY now has more entries)
    # Both outcomes are "consistent" as long as Post didn't bypass the closed flag check without locking.

    r_close, r_post = responses[0], responses[1]

    if r_post.status_code == 200:
        # Post succeeded, then close must have seen the updated state
        assert r_close.status_code == 200
    else:
        # Post failed, must be because close committed first
        assert "closed" in r_post.json()["message"].lower()
