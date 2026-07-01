import asyncio
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_parallel_sales_invoice_posting_no_negative_stock(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Ensure that concurrent sales posting doesn't lead to negative stock."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    item_id = erp_seed["item"].id
    warehouse_id = erp_seed["warehouse"].id
    party_id = erp_seed["party"].id

    # 1. First, ensure we have some stock (e.g., 10 units)
    # We can do this via a Purchase Invoice or direct seed.
    # multi_company_seed doesn't add stock. erp_seed has some?
    # Let's check erp_seed or create a Purchase first.

    # Create Purchase to get 10 units
    pur_payload = {
        "party_id": str(party_id),
        "document_type": "PURCHASE",
        "invoice_date": "2025-06-01",
        "items": [
            {
                "item_name": "Test Item",
                "stock_item_id": str(item_id),
                "warehouse_id": str(warehouse_id),
                "quantity": 10,
                "rate": 100,
                "tax_rate": 0
            }
        ]
    }
    res = await client.post(
        "/api/v1/billing/invoices",
        json=pur_payload,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )
    inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # 2. Parallel Sales: 3 requests selling 5 units each (Total 15 > 10)
    # Exactly 2 should succeed, 1 should fail.

    async def create_and_post_sale():
        sale_payload = {
            "party_id": str(party_id),
            "document_type": "SALES",
            "invoice_date": "2025-06-02",
            "items": [
                {
                    "item_name": "Test Item",
                    "stock_item_id": str(item_id),
                    "warehouse_id": str(warehouse_id),
                    "quantity": 5,
                    "rate": 200,
                    "tax_rate": 0
                }
            ]
        }
        res = await client.post(
            "/api/v1/billing/invoices",
            json=sale_payload,
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
        )
        if res.status_code != 201: return res
        inv_id = res.json()["data"]["id"]
        return await client.post(
            f"/api/v1/billing/invoices/{inv_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )

    tasks = [create_and_post_sale() for _ in range(3)]
    responses = await asyncio.gather(*tasks)

    successes = [r for r in responses if r.status_code == 200]
    failures = [r for r in responses if r.status_code == 400]

    assert len(successes) == 2
    assert len(failures) == 1
    assert "negative stock" in failures[0].json()["message"].lower()
