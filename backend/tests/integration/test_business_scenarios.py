import pytest
from httpx import AsyncClient
from datetime import date
from app.shared.constants.business import DocumentType
from app.core.security import create_access_token


@pytest.mark.anyio
async def test_complete_purchase_to_sale_flow(client: AsyncClient, erp_seed, db):
    token = create_access_token(erp_seed["user"].id)
    headers = {"Authorization": f"Bearer {token}", "X-Company-ID": str(erp_seed["company"].id)}

    # SCENARIO 1: Purchase 100 units @ 10
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": DocumentType.PURCHASE,
        "invoice_date": str(date.today()),
        "items": [
            {
                "stock_item_id": str(erp_seed["item"].id),
                "warehouse_id": str(erp_seed["warehouse"].id),
                "item_name": "Widget",
                "quantity": 100,
                "rate": 10,
                "tax_rate": 0
            }
        ]
    }

    # Create & Post Purchase
    res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
    assert res.status_code == 201
    inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

    # Verify Stock = 100, WAC = 10
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 100.0
    assert float(erp_seed["item"].average_cost) == 10.0

    # SCENARIO 2: Purchase 100 units @ 20
    payload["items"][0]["rate"] = 20
    res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
    inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

    # Verify Stock = 200, WAC = 15
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 200.0
    assert float(erp_seed["item"].average_cost) == 15.0

    # SCENARIO 3: Sell 50 units
    payload_sale = {
        "party_id": str(erp_seed["party"].id),
        "document_type": DocumentType.SALES,
        "invoice_date": str(date.today()),
        "items": [
            {
                "stock_item_id": str(erp_seed["item"].id),
                "warehouse_id": str(erp_seed["warehouse"].id),
                "item_name": "Widget",
                "quantity": 50,
                "rate": 30, # Sale rate doesn't affect WAC
                "tax_rate": 0
            }
        ]
    }
    res = await client.post("/api/v1/billing/invoices", json=payload_sale, headers=headers)
    inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

    # Verify Stock = 150, WAC = 15
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 150.0
    assert float(erp_seed["item"].average_cost) == 15.0

    # SCENARIO 4: Cancel Sale
    await client.post(f"/api/v1/billing/invoices/{inv_id}/cancel", headers=headers)

    # Verify Stock = 200, WAC = 15
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 200.0
    assert float(erp_seed["item"].average_cost) == 15.0
