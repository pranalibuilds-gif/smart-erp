import pytest
import uuid
from httpx import AsyncClient
from app.core.security import create_access_token
from app.shared.constants.business import InvoiceStatus

@pytest.mark.asyncio
async def test_illegal_invoice_state_transitions(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """
    Stage 3: State Transition Audit.
    Attempt invalid transitions for Invoices.
    """
    company_id = erp_seed["company"].id
    headers = {"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}

    # Create Draft
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "invoice_date": "2025-06-01",
        "items": [{"item_name": "Test", "quantity": 1, "rate": 100, "tax_rate": 0}]
    }
    res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
    inv_id = res.json()["data"]["id"]

    # 1. ATTEMPT: Cancel -> Post (ILLEGAL)
    await client.post(f"/api/v1/billing/invoices/{inv_id}/cancel", headers=headers)
    res = await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)
    assert res.status_code == 400
    assert "only draft" in res.json()["message"].lower()

@pytest.mark.asyncio
async def test_transactional_rollback_failure_injection(client: AsyncClient, erp_seed: dict, admin_token: str, db):
    """
    Stage 4: Failure Injection.
    Simulate a failure during invoice posting and verify rollback.
    """
    company_id = erp_seed["company"].id
    headers = {"Authorization": f"Bearer {admin_token}", "X-Company-ID": str(company_id)}

    # Setup: Create a draft invoice
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "invoice_date": "2025-06-01",
        "items": [{"stock_item_id": str(erp_seed["item"].id), "warehouse_id": str(erp_seed["warehouse"].id), "item_name": "Test", "quantity": 1, "rate": 100, "tax_rate": 0}]
    }
    res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
    inv_id = res.json()["data"]["id"]

    # We will "break" the Voucher numbering or something that happens after Invoice.status change
    # But wait, InvoiceService.post_invoice uses a single transaction.
    # If any part fails, the whole thing should rollback.

    # ATTACK: Attempt to post with NEGATIVE stock (this triggers an exception in InventoryPostingService)
    # We already have a widget count of 0. Posting 1 widget sale will fail.
    # We want to ensure the Invoice status remains DRAFT and no Voucher is created.

    res = await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)
    assert res.status_code == 400 # Negative stock error

    # VERIFY ROLLBACK:
    # 1. Invoice must still be DRAFT
    res_inv = await client.get(f"/api/v1/billing/invoices/{inv_id}", headers=headers)
    assert res_inv.json()["data"]["status"] == "DRAFT"
    assert res_inv.json()["data"]["voucher_id"] is None

    # 2. No voucher should have been created (harder to check via API if we don't know the ID,
    # but we can check the total voucher count)
    res_v = await client.get("/api/v1/vouchers", headers=headers)
    assert len(res_v.json()["data"]) == 0
