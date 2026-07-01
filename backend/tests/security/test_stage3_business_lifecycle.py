import pytest
import uuid
from httpx import AsyncClient
from datetime import date
from decimal import Decimal
from app.core.security import create_access_token
from app.shared.constants.business import DocumentType, VoucherStatus, InvoiceStatus

@pytest.mark.asyncio
async def test_scenario_a_retail_lifecycle(client: AsyncClient, erp_seed: dict, db):
    """
    Stage 1, Scenario A: Comprehensive Retail Business Lifecycle.
    Purchase -> Payment -> Sale -> Receipt -> Transfer -> Close FY.
    """
    token = create_access_token(erp_seed["user"].id)
    headers = {"Authorization": f"Bearer {token}", "X-Company-ID": str(erp_seed["company"].id)}

    # 1. SETUP: We have erp_seed providing Company, FY, Party, Item, Warehouse
    item = erp_seed["item"]
    warehouse = erp_seed["warehouse"]
    party = erp_seed["party"]

    # 2. PURCHASE: Buy 100 units @ 10
    purchase_payload = {
        "party_id": str(party.id),
        "document_type": "PURCHASE",
        "invoice_date": "2025-04-10",
        "items": [
            {
                "stock_item_id": str(item.id),
                "warehouse_id": str(warehouse.id),
                "item_name": "Widget",
                "quantity": 100,
                "rate": 10,
                "tax_rate": 0
            }
        ]
    }
    res = await client.post("/api/v1/billing/invoices", json=purchase_payload, headers=headers)
    assert res.status_code == 201
    pur_inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{pur_inv_id}/post", headers=headers)

    # Assert Inventory
    await db.refresh(item)
    assert float(item.current_quantity) == 100.0

    # 3. PARTIAL PAYMENT: Pay 400 for the 1000 invoice
    pay_payload = {
        "bank_cash_ledger_id": str(erp_seed["cap_ledger"].id), # Seeded ledger used as cash
        "party_ledger_id": str(party.ledger_id),
        "amount": 400,
        "voucher_date": "2025-04-12",
        "allocations": [
            {"invoice_id": pur_inv_id, "allocated_amount": 400}
        ]
    }
    res = await client.post("/api/v1/banking/payments", json=pay_payload, headers=headers)
    assert res.status_code == 201

    # Assert Outstanding
    res = await client.get(f"/api/v1/banking/invoices/{pur_inv_id}/outstanding", headers=headers)
    assert float(res.json()["data"]) == 600.0

    # 4. SALE: Sell 20 units @ 25
    sale_payload = {
        "party_id": str(party.id),
        "document_type": "SALES",
        "invoice_date": "2025-05-01",
        "items": [
            {
                "stock_item_id": str(item.id),
                "warehouse_id": str(warehouse.id),
                "item_name": "Widget",
                "quantity": 20,
                "rate": 25,
                "tax_rate": 0
            }
        ]
    }
    res = await client.post("/api/v1/billing/invoices", json=sale_payload, headers=headers)
    assert res.status_code == 201
    sale_inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{sale_inv_id}/post", headers=headers)

    # Assert Inventory
    await db.refresh(item)
    assert float(item.current_quantity) == 80.0

    # 5. TRANSFER: Move 30 units to another warehouse
    # Create new warehouse
    res = await client.post("/api/v1/masters/warehouses", json={"name": "Branch", "code": "BR01"}, headers=headers)
    wh_branch_id = res.json()["data"]["id"]

    transfer_payload = {
        "from_warehouse_id": str(warehouse.id),
        "to_warehouse_id": wh_branch_id,
        "transfer_date": "2025-05-15",
        "items": [
            {"stock_item_id": str(item.id), "quantity": 30}
        ]
    }
    res = await client.post("/api/v1/inventory/transfers", json=transfer_payload, headers=headers)
    assert res.status_code == 201
    trn_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/inventory/transfers/{trn_id}/post", headers=headers)

    # Assert Warehouse Distribution
    res = await client.get(f"/api/v1/reports/warehouse-stock/{warehouse.id}", headers=headers)
    # Filter for our item
    wh_main_item = next(i for i in res.json()["data"]["items"] if i["item_id"] == str(item.id))
    assert float(wh_main_item["quantity"]) == 50.0

    res = await client.get(f"/api/v1/reports/warehouse-stock/{wh_branch_id}", headers=headers)
    wh_branch_item = next(i for i in res.json()["data"]["items"] if i["item_id"] == str(item.id))
    assert float(wh_branch_item["quantity"]) == 30.0

    # 6. YEAR CLOSING: Simulate month-end then close
    # (Simplified: close the year)
    res = await client.post(f"/api/v1/companies/{erp_seed['company'].id}/financial-years/{erp_seed['fy'].id}/close", headers=headers)
    assert res.status_code == 200

    # Assert that a new FY was created
    res = await client.get(f"/api/v1/companies/{erp_seed['company'].id}/financial-years", headers=headers)
    assert len(res.json()["data"]) == 2

    # 7. FINAL INTEGRITY CHECK: Trial Balance must be balanced
    res = await client.get("/api/v1/reports/trial-balance", headers=headers)
    assert res.json()["data"]["is_balanced"] is True
