import pytest
from httpx import AsyncClient
import uuid
from decimal import Decimal

@pytest.mark.asyncio
async def test_wac_calculation_accuracy(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Verify WAC calculation with multiple purchases at different rates."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    party_id = erp_seed["party"].id
    item_id = erp_seed["item"].id
    warehouse_id = erp_seed["warehouse"].id

    # 1. Purchase 10 units @ 100
    pur1 = {
        "party_id": str(party_id),
        "document_type": "PURCHASE",
        "items": [{"item_name": "Widget", "stock_item_id": str(item_id), "warehouse_id": str(warehouse_id), "quantity": 10, "rate": 100, "tax_rate": 0}]
    }
    res = await client.post("/api/v1/billing/invoices", json=pur1, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    await client.post(f"/api/v1/billing/invoices/{res.json()['data']['id']}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # Verify WAC is 100
    res = await client.get("/api/v1/masters/stock-items", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    item = next(i for i in res.json()["data"] if i["id"] == str(item_id))
    assert item["average_cost"] == 100.0

    # 2. Purchase 1 unit @ 1000
    pur2 = {
        "party_id": str(party_id),
        "document_type": "PURCHASE",
        "items": [{"item_name": "Widget", "stock_item_id": str(item_id), "warehouse_id": str(warehouse_id), "quantity": 1, "rate": 1000, "tax_rate": 0}]
    }
    res = await client.post("/api/v1/billing/invoices", json=pur2, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    await client.post(f"/api/v1/billing/invoices/{res.json()['data']['id']}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # Expected WAC: (10*100 + 1*1000) / 11 = 2000 / 11 = 181.818...
    res = await client.get("/api/v1/masters/stock-items", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    item = next(i for i in res.json()["data"] if i["id"] == str(item_id))
    assert abs(item["average_cost"] - 181.818181) < 0.01

    # 3. Sale should NOT change WAC
    sale = {
        "party_id": str(party_id),
        "document_type": "SALES",
        "items": [{"item_name": "Widget", "stock_item_id": str(item_id), "warehouse_id": str(warehouse_id), "quantity": 5, "rate": 500, "tax_rate": 0}]
    }
    res = await client.post("/api/v1/billing/invoices", json=sale, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    await client.post(f"/api/v1/billing/invoices/{res.json()['data']['id']}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    res = await client.get("/api/v1/masters/stock-items", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    item = next(i for i in res.json()["data"] if i["id"] == str(item_id))
    assert abs(item["average_cost"] - 181.818181) < 0.01
