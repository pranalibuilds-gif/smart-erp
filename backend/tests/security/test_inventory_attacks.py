import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_warehouse_isolation_sales(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Selling from a warehouse with zero stock should fail even if other warehouses have stock."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    item_id = erp_seed["item"].id
    warehouse_id = erp_seed["warehouse"].id # This WH is empty
    party_id = erp_seed["party"].id

    # Create Sales Invoice from empty warehouse
    sale_data = {
        "party_id": str(party_id),
        "document_type": "SALES",
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

    # Creation as draft might succeed, but posting should fail
    response = await client.post(
        "/api/v1/billing/invoices",
        json=sale_data,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )

    if response.status_code == 201:
        inv_id = response.json()["data"]["id"]
        # Try to post
        response = await client.post(
            f"/api/v1/billing/invoices/{inv_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )

    assert response.status_code == 400
    assert "negative stock" in response.json()["message"].lower()
