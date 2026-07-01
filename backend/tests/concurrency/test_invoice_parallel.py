import asyncio
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_parallel_same_invoice_posting(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Ensure that posting the same invoice twice concurrently only creates one set of accounting entries."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 1. Create a draft invoice
    invoice_payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "invoice_date": "2025-06-01",
        "items": [
            {
                "item_name": "Test Item",
                "quantity": 1,
                "rate": 100,
                "tax_rate": 0
            }
        ]
    }
    res = await client.post(
        "/api/v1/billing/invoices",
        json=invoice_payload,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )
    inv_id = res.json()["data"]["id"]

    # 2. Parallel Posting requests
    async def post_invoice():
        return await client.post(
            f"/api/v1/billing/invoices/{inv_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )

    tasks = [post_invoice() for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    successes = [r for r in responses if r.status_code == 200]
    failures = [r for r in responses if r.status_code == 400]

    assert len(successes) == 1
    # Subsequent requests should fail with "Only draft invoices can be posted" or similar
    assert len(failures) == 4
    assert "draft" in failures[0].json()["message"].lower()
