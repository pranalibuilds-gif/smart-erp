import pytest
from httpx import AsyncClient
import uuid
from decimal import Decimal

@pytest.mark.asyncio
async def test_partial_payment_workflow(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Test multi-step partial payments and verify outstanding balance."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    party = erp_seed["party"]
    item = erp_seed["item"]
    warehouse = erp_seed["warehouse"]

    # 1. Create and Post a Sales Invoice for 1000
    invoice_payload = {
        "party_id": str(party.id),
        "document_type": "SALES",
        "invoice_date": "2025-06-01",
        "items": [
            {
                "item_name": "Widget",
                "stock_item_id": str(item.id),
                "warehouse_id": str(warehouse.id),
                "quantity": 10,
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
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # Verify initial outstanding
    res = await client.get(f"/api/v1/banking/invoices/{inv_id}/outstanding", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    assert res.json()["data"] == 1000.0

    # 2. First Partial Payment: 300
    payment_1 = {
        "party_ledger_id": str(party.ledger_id),
        "bank_cash_ledger_id": str(erp_seed["sales_ledger"].id), # dummy bank
        "amount": 300,
        "payment_date": "2025-06-02",
        "allocations": [{"invoice_id": inv_id, "allocated_amount": 300}]
    }
    await client.post("/api/v1/banking/receipts", json=payment_1, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})

    res = await client.get(f"/api/v1/banking/invoices/{inv_id}/outstanding", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    assert res.json()["data"] == 700.0

    # 3. Second Partial Payment: 400
    payment_2 = {
        "party_ledger_id": str(party.ledger_id),
        "bank_cash_ledger_id": str(erp_seed["sales_ledger"].id),
        "amount": 400,
        "payment_date": "2025-06-03",
        "allocations": [{"invoice_id": inv_id, "allocated_amount": 400}]
    }
    await client.post("/api/v1/banking/receipts", json=payment_2, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})

    res = await client.get(f"/api/v1/banking/invoices/{inv_id}/outstanding", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    assert res.json()["data"] == 300.0

    # 4. Over-allocation attempt: try to pay 500 when only 300 is left
    payment_3 = {
        "party_ledger_id": str(party.ledger_id),
        "bank_cash_ledger_id": str(erp_seed["sales_ledger"].id),
        "amount": 500,
        "payment_date": "2025-06-04",
        "allocations": [{"invoice_id": inv_id, "allocated_amount": 500}]
    }
    res = await client.post("/api/v1/banking/receipts", json=payment_3, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})

    # This should fail if we've hardened it
    assert res.status_code == 400
    assert "exceeds outstanding" in res.json()["message"].lower()

@pytest.mark.asyncio
async def test_multi_invoice_allocation(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Test allocating one receipt to multiple invoices."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    party = erp_seed["party"]

    # Create 2 invoices for 500 each
    async def create_inv(amount):
        payload = {
            "party_id": str(party.id),
            "document_type": "SALES",
            "items": [{"item_name": "Item", "quantity": 1, "rate": amount, "tax_rate": 0}]
        }
        r = await client.post("/api/v1/billing/invoices", json=payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
        id = r.json()["data"]["id"]
        await client.post(f"/api/v1/billing/invoices/{id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
        return id

    inv1 = await create_inv(500)
    inv2 = await create_inv(500)

    # Pay 800: 500 to inv1, 300 to inv2
    receipt = {
        "party_ledger_id": str(party.ledger_id),
        "bank_cash_ledger_id": str(erp_seed["sales_ledger"].id),
        "amount": 800,
        "payment_date": "2025-06-05",
        "allocations": [
            {"invoice_id": inv1, "allocated_amount": 500},
            {"invoice_id": inv2, "allocated_amount": 300}
        ]
    }
    res = await client.post("/api/v1/banking/receipts", json=receipt, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    assert res.status_code == 201

    # Check outstandings
    res1 = await client.get(f"/api/v1/banking/invoices/{inv1}/outstanding", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    res2 = await client.get(f"/api/v1/banking/invoices/{inv2}/outstanding", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    assert res1.json()["data"] == 0.0
    assert res2.json()["data"] == 200.0
