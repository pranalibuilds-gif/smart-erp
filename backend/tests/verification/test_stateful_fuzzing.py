import pytest
import random
import uuid
from httpx import AsyncClient
from datetime import date

@pytest.mark.asyncio
async def test_stateful_workflow_fuzzing(client: AsyncClient, erp_seed: dict, admin_token: str):
    """
    Phase 6: Stateful Fuzzing.
    Randomly executes business operations and verifies aggregate stability.
    """
    headers = {"Authorization": f"Bearer {admin_token}", "X-Company-ID": str(erp_seed["company"].id)}

    # 1. Gather master IDs
    res = await client.get("/api/v1/masters/warehouses", headers=headers)
    warehouses = [w["id"] for w in res.json()["data"]]

    res = await client.get("/api/v1/masters/stock-items", headers=headers)
    stock_items = [i["id"] for i in res.json()["data"]]

    res = await client.get("/api/v1/parties", headers=headers)
    parties = [p["id"] for p in res.json()["data"]]

    invoices = []
    transfers = []

    # 2. Fuzzing Loop (50 iterations)
    for _ in range(50):
        op = random.randint(1, 6)

        if op == 1: # Create Invoice
            payload = {
                "party_id": random.choice(parties),
                "document_type": random.choice(["SALES", "PURCHASE"]),
                "invoice_date": str(date.today()),
                "items": [{
                    "stock_item_id": random.choice(stock_items),
                    "warehouse_id": random.choice(warehouses),
                    "item_name": "Fuzz",
                    "quantity": random.randint(1, 10),
                    "rate": random.randint(10, 100),
                    "tax_rate": 0
                }]
            }
            res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
            if res.status_code == 201:
                invoices.append(res.json()["data"]["id"])

        elif op == 2 and invoices: # Post Invoice
            inv_id = random.choice(invoices)
            await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

        elif op == 3 and invoices: # Cancel Invoice
            inv_id = random.choice(invoices)
            await client.post(f"/api/v1/billing/invoices/{inv_id}/cancel", headers=headers)

        elif op == 4: # Create Transfer
            if len(warehouses) < 2: continue
            w1, w2 = random.sample(warehouses, 2)
            payload = {
                "from_warehouse_id": w1,
                "to_warehouse_id": w2,
                "transfer_date": str(date.today()),
                "items": [{"stock_item_id": random.choice(stock_items), "quantity": random.randint(1, 2)}]
            }
            res = await client.post("/api/v1/inventory/transfers", json=payload, headers=headers)
            if res.status_code == 201:
                transfers.append(res.json()["data"]["id"])

        elif op == 5 and transfers: # Post Transfer
            t_id = random.choice(transfers)
            await client.post(f"/api/v1/inventory/transfers/{t_id}/post", headers=headers)

        elif op == 6 and transfers: # Cancel Transfer
            t_id = random.choice(transfers)
            await client.post(f"/api/v1/inventory/transfers/{t_id}/cancel", headers=headers)

    # 3. VERIFY STABILITY
    # Trial Balance must be balanced
    res = await client.get("/api/v1/reports/trial-balance", headers=headers)
    assert res.json()["data"]["is_balanced"] is True

    # Financial Statements should not crash
    res = await client.get("/api/v1/reports/balance-sheet", headers=headers)
    assert res.status_code == 200
