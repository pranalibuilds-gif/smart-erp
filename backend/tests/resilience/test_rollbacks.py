import pytest
from httpx import AsyncClient
from unittest.mock import patch
from sqlalchemy import select
from app.modules.vouchers.models import Voucher
from app.modules.billing.models import Invoice
from app.shared.constants.business import InvoiceStatus

@pytest.mark.asyncio
async def test_invoice_post_rollback_on_inventory_failure(client: AsyncClient, accountant_token: str, erp_seed: dict, db):
    """If inventory posting fails, the entire invoice posting must roll back."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 1. Create a draft invoice
    invoice_payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "items": [{"item_name": "Item", "quantity": 1, "rate": 100, "stock_item_id": str(erp_seed["item"].id), "warehouse_id": str(erp_seed["warehouse"].id)}]
    }
    res = await client.post("/api/v1/billing/invoices", json=invoice_payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    inv_id = res.json()["data"]["id"]

    # 2. Simulate failure in InventoryPostingService
    with patch("app.modules.vouchers.service.InventoryPostingService.post_inventory", side_effect=Exception("Simulated Inventory Failure")):
        response = await client.post(
            f"/api/v1/billing/invoices/{inv_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )
        assert response.status_code == 500

    # 3. Verify Rollback
    db.expire_all()
    # Invoice should still be DRAFT
    stmt = select(Invoice).where(Invoice.id == inv_id)
    res_inv = await db.execute(stmt)
    invoice = res_inv.scalar_one()
    assert invoice.status == InvoiceStatus.DRAFT
    assert invoice.voucher_id is None

    # No Voucher should exist (it was created but should have rolled back)
    stmt = select(Voucher).where(Voucher.narration.like(f"%{inv_id}%"))
    res_v = await db.execute(stmt)
    assert res_v.scalar_one_or_none() is None
