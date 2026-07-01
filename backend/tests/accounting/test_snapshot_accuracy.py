import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_item_snapshot_accuracy(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Verify that renaming a stock item doesn't change historical invoice item names."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    item_id = erp_seed["item"].id
    warehouse_id = erp_seed["warehouse"].id

    # 1. Create Invoice with "Widget"
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "items": [{"item_name": "Widget", "stock_item_id": str(item_id), "warehouse_id": str(warehouse_id), "quantity": 1, "rate": 100}]
    }
    res = await client.post("/api/v1/billing/invoices", json=payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    inv_id = res.json()["data"]["id"]

    # 2. Rename Stock Item to "Grommet"
    # Assuming PATCH /api/v1/masters/stock-items/{id}
    await client.patch(
        f"/api/v1/masters/stock-items/{item_id}",
        json={"name": "Grommet"},
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )

    # 3. Verify Invoice still says "Widget"
    res = await client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    item = res.json()["data"]["items"][0]
    assert item["item_name"] == "Widget"
    # But stock_item_id still points to the same object
    assert item["stock_item_id"] == str(item_id)
