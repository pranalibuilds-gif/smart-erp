import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.models import User
from app.modules.companies.models import Company

@pytest.mark.asyncio
async def test_negative_quantity_in_voucher_denied(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """
    Attack: Attempt to record -100 quantity (Purchase) to "gain" stock without paying.
    """
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    item_id = erp_seed["item"].id
    wh_id = erp_seed["warehouse"].id
    ledger_id = erp_seed["pur_ledger"].id
    cash_id = erp_seed["cap_ledger"].id # Simplified

    payload = {
        "voucher_type": "PURCHASE",
        "voucher_date": "2025-06-01",
        "entries": [
            {"ledger_id": str(ledger_id), "debit_amount": -1000, "credit_amount": 0},
            {"ledger_id": str(cash_id), "debit_amount": 0, "credit_amount": -1000}
        ],
        "inventory_entries": [
            {"stock_item_id": str(item_id), "warehouse_id": str(wh_id), "quantity": -10, "rate": 100}
        ]
    }

    response = await client.post(
        "/api/v1/vouchers",
        json=payload,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )

    # Should be rejected (400 or 422)
    assert response.status_code in [400, 422]

@pytest.mark.asyncio
async def test_post_to_closed_financial_year_denied(client: AsyncClient, admin_token: str, erp_seed: dict):
    """
    Attack: Close FY, then attempt to post a new voucher to it.
    """
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # 1. Close FY
    await client.post(
        f"/api/v1/companies/{company_id}/financial-years/{fy_id}/close",
        headers={"Authorization": f"Bearer {admin_token}", "X-Company-ID": str(company_id)}
    )

    # 2. Attempt to create voucher in that FY
    payload = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2025-06-01",
        "entries": [
            {"ledger_id": str(erp_seed["sales_ledger"].id), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 0, "credit_amount": 100}
        ]
    }

    response = await client.post(
        "/api/v1/vouchers",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )

    assert response.status_code == 400
    assert "closed" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_negative_stock_prevention_on_post(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """
    Attack: Post a Sales voucher that exceeds available quantity.
    """
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    item_id = erp_seed["item"].id
    wh_id = erp_seed["warehouse"].id

    # User has 0 widgets. Attempt to sell 1.
    payload = {
        "voucher_type": "SALES",
        "voucher_date": "2025-06-01",
        "entries": [
            {"ledger_id": str(erp_seed["sales_ledger"].id), "debit_amount": 0, "credit_amount": 100},
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 100, "credit_amount": 0}
        ],
        "inventory_entries": [
            {"stock_item_id": str(item_id), "warehouse_id": str(wh_id), "quantity": 1, "rate": 100}
        ]
    }

    # 1. Create Draft (Might be allowed depending on policy, but POST should fail)
    res = await client.post(
        "/api/v1/vouchers",
        json=payload,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )
    v_id = res.json()["data"]["id"]

    # 2. Post Voucher
    response = await client.post(
        f"/api/v1/vouchers/{v_id}/post",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )

    assert response.status_code == 400
    assert "negative stock" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_zero_rate_wac_attack(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """
    Attack: Inward transaction with 0 rate to drop the average cost to near-zero.
    """
    # This is more of a business sanity check.
    # Usually ERPs allow 0 rate for samples/bonuses.
    pass
