import pytest
from httpx import AsyncClient
from unittest.mock import patch
from sqlalchemy import select
from app.modules.vouchers.models import Voucher
from app.shared.constants.business import VoucherStatus

@pytest.mark.asyncio
async def test_voucher_post_succeeds_even_if_audit_fails(client: AsyncClient, accountant_token: str, erp_seed: dict, db):
    """Business transactions should succeed even if the audit log fails (soft-fail)."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 1. Create a draft voucher
    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [
            {"ledger_id": str(erp_seed["sales_ledger"].id), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 0, "credit_amount": 100}
        ]
    }
    res = await client.post("/api/v1/vouchers", json=voucher_data, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    v_id = res.json()["data"]["id"]

    # 2. Simulate failure in AuditService
    with patch("app.modules.vouchers.service.AuditService.log_action", side_effect=Exception("Audit Backend Unreachable")):
        response = await client.post(
            f"/api/v1/vouchers/{v_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )
        # It should still be 200 OK because of soft-fail implementation
        assert response.status_code == 200

    # 3. Verify Persistence
    db.expire_all()
    stmt = select(Voucher).where(Voucher.id == v_id)
    res_v = await db.execute(stmt)
    voucher = res_v.scalar_one()
    assert voucher.status == VoucherStatus.POSTED

@pytest.mark.asyncio
async def test_invoice_post_succeeds_even_if_search_index_fails(client: AsyncClient, accountant_token: str, erp_seed: dict, db):
    """Business transactions should succeed even if search indexing fails."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    invoice_payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "items": [{"item_name": "Item", "quantity": 1, "rate": 100}]
    }
    res = await client.post("/api/v1/billing/invoices", json=invoice_payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
    inv_id = res.json()["data"]["id"]

    # 2. Simulate failure in SearchService
    with patch("app.modules.billing.service.SearchService.update_index", side_effect=Exception("Search Index Down")):
        response = await client.post(
            f"/api/v1/billing/invoices/{inv_id}/post",
            headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
        )
        assert response.status_code == 200
