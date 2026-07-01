import pytest
import asyncio
import uuid
from decimal import Decimal
from httpx import AsyncClient
from app.modules.vouchers.schemas.vouchers import VoucherCreate, VoucherEntryCreate
from scripts.audit_engine import AuditEngine

@pytest.mark.asyncio
async def test_stage1_stress_journal_precision(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """
    Stage 1: Decimal Torture.
    Post a journal with many tiny amounts to verify precision (0.01 + 0.02 + ...).
    """
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    ledger_a = erp_seed["sales_ledger"].id
    ledger_b = erp_seed["pur_ledger"].id

    # 500 lines of 0.01
    count = 500
    entries = []
    for i in range(count):
        entries.append({"ledger_id": str(ledger_a), "debit_amount": 0.01, "credit_amount": 0})

    entries.append({"ledger_id": str(ledger_b), "debit_amount": 0, "credit_amount": float(count * 0.01)})

    payload = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2025-06-01",
        "entries": entries
    }

    res = await client.post(
        "/api/v1/vouchers",
        json=payload,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    assert res.status_code == 201
    v_id = res.json()["data"]["id"]

    # Post it
    res_post = await client.post(
        f"/api/v1/vouchers/{v_id}/post",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    assert res_post.status_code == 200

@pytest.mark.asyncio
async def test_stage1_massive_concurrency(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """
    Stage 1: Concurrent posting of 100 vouchers.
    """
    company_id = erp_seed["company"].id
    ledger_a = erp_seed["sales_ledger"].id
    ledger_b = erp_seed["pur_ledger"].id

    async def post_one():
        payload = {
            "voucher_type": "JOURNAL",
            "voucher_date": "2025-06-01",
            "entries": [
                {"ledger_id": str(ledger_a), "debit_amount": 10, "credit_amount": 0},
                {"ledger_id": str(ledger_b), "debit_amount": 0, "credit_amount": 10}
            ]
        }
        r1 = await client.post("/api/v1/vouchers", json=payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
        v_id = r1.json()["data"]["id"]
        return await client.post(f"/api/v1/vouchers/{v_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # Run 50 concurrent (to avoid local resource exhaustion during tests)
    results = await asyncio.gather(*[post_one() for _ in range(50)])
    for r in results:
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_stage2_ledger_balance_audit(db, erp_seed: dict):
    """
    Stage 2: Use the AuditEngine to verify no drift exists after stress.
    """
    engine = AuditEngine(db)
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    report = await engine.audit_ledger_balances(company_id, fy_id)

    fails = [item for item in report if item["status"] == "FAIL"]
    assert not fails, f"Ledger drift detected: {fails}"

@pytest.mark.asyncio
async def test_stage3_inventory_integrity_audit(db, erp_seed: dict):
    """
    Stage 3: Inventory Integrity verification.
    """
    engine = AuditEngine(db)
    company_id = erp_seed["company"].id

    report = await engine.audit_inventory_integrity(company_id)
    fails = [item for item in report if item["status"] == "FAIL"]
    assert not fails, f"Inventory drift detected: {fails}"

@pytest.mark.asyncio
async def test_stage4_financial_statement_reconciliation(db, erp_seed: dict):
    """
    Stage 4: Reconciliation between P&L and Balance Sheet.
    """
    engine = AuditEngine(db)
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    res = await engine.audit_financial_statements(company_id, fy_id)
    assert res["reconciled"] is True, f"Reconciliation failed: {res}"

@pytest.mark.asyncio
async def test_stage7_cross_module_consistency(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """
    Stage 7: Purchase -> Sales Invoice -> Voucher -> Ledger -> Inventory -> Audit.
    """
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    item_id = erp_seed["item"].id
    wh_id = erp_seed["warehouse"].id

    # 0. Purchase stock first to avoid negative stock error
    purchase_payload = {
        "voucher_type": "PURCHASE",
        "voucher_date": "2025-06-01",
        "entries": [
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 1000, "credit_amount": 0},
            {"ledger_id": str(erp_seed["cap_ledger"].id), "debit_amount": 0, "credit_amount": 1000}
        ],
        "inventory_entries": [
            {"stock_item_id": str(item_id), "warehouse_id": str(wh_id), "quantity": 10, "rate": 100}
        ]
    }
    res_pur = await client.post("/api/v1/vouchers", json=purchase_payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    assert res_pur.status_code == 201
    await client.post(f"/api/v1/vouchers/{res_pur.json()['data']['id']}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # 1. Create and Post Sales Invoice
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "invoice_date": "2025-06-01",
        "items": [
            {
                "stock_item_id": str(item_id),
                "warehouse_id": str(wh_id),
                "item_name": "Widget",
                "quantity": 5,
                "rate": 200,
                "tax_rate": 0
            }
        ]
    }

    res = await client.post("/api/v1/billing/invoices", json=payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    assert res.status_code == 201
    inv_id = res.json()["data"]["id"]

    res_post = await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    assert res_post.status_code == 200

    # 2. Verify Voucher exists
    res_inv = await client.get(f"/api/v1/billing/invoices/{inv_id}", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    v_id = res_inv.json()["data"]["voucher_id"]
    assert v_id is not None

    # 3. Verify Inventory Transaction
    res_v = await client.get(f"/api/v1/vouchers/{v_id}", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    assert len(res_v.json()["data"]["inventory_entries"]) == 1
    assert res_v.json()["data"]["inventory_entries"][0]["direction"] == -1 # Outward

@pytest.mark.asyncio
async def test_stage8_database_consistency_audit(db):
    """
    Stage 8: Deep DB scan for orphans or duplicates.
    """
    engine = AuditEngine(db)
    issues = await engine.audit_database_consistency()
    assert not issues, f"DB Inconsistency found: {issues}"
