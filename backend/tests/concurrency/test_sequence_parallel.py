import asyncio
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_parallel_voucher_numbering(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Stress test the voucher sequence generator to ensure no duplicate numbers."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    ledger_a = erp_seed["sales_ledger"].id
    ledger_b = erp_seed["pur_ledger"].id

    num_requests = 20 # Start with 20 parallel requests

    async def create_voucher():
        voucher_data = {
            "voucher_type": "JOURNAL",
            "voucher_date": "2024-06-01",
            "entries": [
                {"ledger_id": str(ledger_a), "debit_amount": 100, "credit_amount": 0},
                {"ledger_id": str(ledger_b), "debit_amount": 0, "credit_amount": 100}
            ]
        }
        return await client.post(
            "/api/v1/vouchers",
            json=voucher_data,
            headers={
                "Authorization": f"Bearer {accountant_token}",
                "X-Company-ID": str(company_id),
                "X-Financial-Year-ID": str(fy_id)
            }
        )

    tasks = [create_voucher() for _ in range(num_requests)]
    responses = await asyncio.gather(*tasks)

    # Check all succeeded
    for r in responses:
        assert r.status_code == 201, r.json()

    # Check for unique voucher numbers
    voucher_numbers = [r.json()["data"]["voucher_number"] for r in responses]
    assert len(set(voucher_numbers)) == num_requests

    # Check for gaps (assuming starting from 0)
    serials = [int(v.split("/")[-1]) for v in voucher_numbers]
    serials.sort()
    assert serials == list(range(1, num_requests + 1))
