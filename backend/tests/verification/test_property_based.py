import pytest
import random
from decimal import Decimal
from httpx import AsyncClient
from app.shared.constants.business import VoucherType

@pytest.mark.asyncio
async def test_accounting_equation_invariant(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """
    Property-Based Test:
    After any number of balanced random journals,
    Trial Balance Total Dr must equal Total Cr.
    """
    headers = {"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(erp_seed["company"].id)}

    # 1. Get available ledgers
    ledgers = [
        erp_seed["sales_ledger"], erp_seed["pur_ledger"], erp_seed["cap_ledger"],
        erp_seed["inv_ledger"], erp_seed["gain_ledger"], erp_seed["loss_ledger"]
    ]

    # 2. Run 50 random balanced journals
    for i in range(50):
        # Pick 2 to 6 random ledgers
        count = random.randint(2, len(ledgers))
        sample = random.sample(ledgers, count)

        amounts = [Decimal(str(random.randint(1, 1000))) for _ in range(count - 1)]
        total = sum(amounts)

        entries = []
        # Assign random Dr/Cr
        for j in range(count - 1):
            if random.choice([True, False]):
                entries.append({"ledger_id": str(sample[j].id), "debit_amount": float(amounts[j]), "credit_amount": 0})
            else:
                entries.append({"ledger_id": str(sample[j].id), "debit_amount": 0, "credit_amount": float(amounts[j])})

        # Calculate last entry to balance
        current_dr = sum(e["debit_amount"] for e in entries)
        current_cr = sum(e["credit_amount"] for e in entries)
        diff = current_dr - current_cr

        if diff > 0: # More Dr, need Cr
            entries.append({"ledger_id": str(sample[-1].id), "debit_amount": 0, "credit_amount": float(diff)})
        else: # More Cr, need Dr
            entries.append({"ledger_id": str(sample[-1].id), "debit_amount": float(abs(diff)), "credit_amount": 0})

        payload = {
            "voucher_type": "JOURNAL",
            "voucher_date": "2025-06-01",
            "entries": entries
        }

        res = await client.post("/api/v1/vouchers", json=payload, headers=headers)
        assert res.status_code == 201
        v_id = res.json()["data"]["id"]
        await client.post(f"/api/v1/vouchers/{v_id}/post", headers=headers)

    # 3. Verify Invariant: Trial Balance is balanced
    res = await client.get("/api/v1/reports/trial-balance", headers=headers)
    assert res.json()["data"]["is_balanced"] is True
    assert abs(res.json()["data"]["total_debit"] - res.json()["data"]["total_credit"]) < 0.01

@pytest.mark.asyncio
async def test_inventory_quantity_invariant(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """
    Property-Based Test:
    Random purchases and sales must result in correct StockBalance
    where Sum(Transactions) == Cached.
    """
    headers = {"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(erp_seed["company"].id)}
    item_id = erp_seed["item"].id
    wh_id = erp_seed["warehouse"].id

    current_qty = 0

    for i in range(30):
        qty = random.randint(1, 20)
        is_purchase = random.choice([True, False])

        if not is_purchase and current_qty < qty:
            is_purchase = True # Force purchase if out of stock

        v_type = "PURCHASE" if is_purchase else "SALES"
        direction = 1 if is_purchase else -1

        payload = {
            "voucher_type": v_type,
            "voucher_date": "2025-06-01",
            "entries": [
                {"ledger_id": str(erp_seed["sales_ledger"].id), "debit_amount": 0 if is_purchase else 100, "credit_amount": 100 if is_purchase else 0},
                {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 100 if is_purchase else 0, "credit_amount": 0 if is_purchase else 100}
            ],
            "inventory_entries": [
                {"stock_item_id": str(item_id), "warehouse_id": str(wh_id), "quantity": qty, "rate": 10}
            ]
        }

        res = await client.post("/api/v1/vouchers", json=payload, headers=headers)
        if res.status_code == 201:
            v_id = res.json()["data"]["id"]
            post_res = await client.post(f"/api/v1/vouchers/{v_id}/post", headers=headers)
            if post_res.status_code == 200:
                current_qty += (qty * direction)

    # Verify Invariant: Report matches calculated
    res = await client.get(f"/api/v1/reports/warehouse-stock/{wh_id}", headers=headers)
    wh_item = next(i for i in res.json()["data"]["items"] if i["item_id"] == str(item_id))
    assert float(wh_item["quantity"]) == float(current_qty)
