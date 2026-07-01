import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.models import User
from app.modules.companies.models import Company

@pytest.mark.asyncio
async def test_cross_tenant_party_in_invoice_denied(client: AsyncClient, multi_company_seed: dict):
    """
    Attack: Create Invoice in Company B, but reference Party from Company A.
    """
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    fy_b_id = multi_company_seed["fy_b"].id
    party_a_id = multi_company_seed["party_a"].id

    payload = {
        "party_id": str(party_a_id),
        "document_type": "SALES",
        "invoice_date": "2025-06-01",
        "items": [
             {
                "item_name": "Ghost Item",
                "quantity": 1,
                "rate": 100,
                "tax_rate": 0
            }
        ]
    }

    response = await client.post(
        "/api/v1/billing/invoices",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id), "X-Financial-Year-ID": str(fy_b_id)}
    )

    # Should be 400 Bad Request (Invalid party)
    assert response.status_code == 400
    assert "invalid party" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_cross_tenant_warehouse_transfer_denied(client: AsyncClient, multi_company_seed: dict):
    """
    Attack: Stock Transfer from Warehouse A (Co A) to Warehouse B (Co B).
    """
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    fy_b_id = multi_company_seed["fy_b"].id
    wh_a_id = multi_company_seed["wh_a"].id
    wh_b_id = multi_company_seed["wh_b"].id
    item_a_id = multi_company_seed["item_a"].id

    payload = {
        "from_warehouse_id": str(wh_a_id), # Co A
        "to_warehouse_id": str(wh_b_id),   # Co B
        "transfer_date": "2025-06-01",
        "items": [
            {"stock_item_id": str(item_a_id), "quantity": 10}
        ]
    }

    response = await client.post(
        "/api/v1/inventory/transfers",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id), "X-Financial-Year-ID": str(fy_b_id)}
    )

    # This might fail (201) if not validated
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_cross_tenant_ledger_reference_in_voucher_denied(client: AsyncClient, multi_company_seed: dict):
    """
    Attack: Voucher in Co B using Ledger from Co A and another valid Ledger from Co B.
    """
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    fy_b_id = multi_company_seed["fy_b"].id
    ledger_a_id = multi_company_seed["ledger_a"].id
    ledger_b_id = multi_company_seed["ledger_b"].id # Assuming seed provides this

    payload = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2025-06-01",
        "entries": [
            {"ledger_id": str(ledger_a_id), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(ledger_b_id), "debit_amount": 0, "credit_amount": 100}
        ]
    }

    response = await client.post(
        "/api/v1/vouchers",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id), "X-Financial-Year-ID": str(fy_b_id)}
    )

    assert response.status_code == 400
    assert "belong to another company" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_audit_log_isolation_verified(client: AsyncClient, multi_company_seed: dict):
    """
    Attack: Request audit logs for a specific entity ID belonging to Co A while in Co B context.
    """
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    ledger_a_id = multi_company_seed["ledger_a"].id

    response = await client.get(
        f"/api/v1/audit/logs?entity_id={ledger_a_id}",
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 0
