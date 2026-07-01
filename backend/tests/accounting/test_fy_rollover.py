import pytest
from httpx import AsyncClient
import uuid
from decimal import Decimal

@pytest.mark.asyncio
async def test_fy_rollover_integrity(client: AsyncClient, accountant_token: str, erp_seed: dict, db):
    """Test that FY rollover correctly carries forward balances and resets P&L."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id
    party_ledger_id = erp_seed["party"].ledger_id
    sales_ledger_id = erp_seed["sales_ledger"].id
    pur_ledger_id = erp_seed["pur_ledger"].id
    cap_ledger_id = erp_seed["cap_ledger"].id

    # 1. Create transactions in current FY
    # Sale: 1000 (Dr Party 1000, Cr Sales 1000)
    # Purchase: 600 (Dr Purchase 600, Cr Party 600)
    # Net Profit = 1000 - 600 = 400.
    # Party Balance = 1000 (Dr) - 600 (Cr) = 400 (Dr).

    async def post_jrn(dr_id, cr_id, amt):
        payload = {
            "voucher_type": "JOURNAL",
            "voucher_date": "2025-06-01",
            "entries": [
                {"ledger_id": str(dr_id), "debit_amount": amt, "credit_amount": 0},
                {"ledger_id": str(cr_id), "debit_amount": 0, "credit_amount": amt}
            ]
        }
        res = await client.post("/api/v1/vouchers", json=payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)})
        v_id = res.json()["data"]["id"]
        await client.post(f"/api/v1/vouchers/{v_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    await post_jrn(party_ledger_id, sales_ledger_id, 1000)
    await post_jrn(pur_ledger_id, party_ledger_id, 600)

    # 2. Close FY
    # Need admin token for this
    admin_token = accountant_token # Fixture has it as owner/admin anyway
    res = await client.post(f"/api/v1/companies/{company_id}/financial-years/{fy_id}/close", headers={"Authorization": f"Bearer {admin_token}", "X-Company-ID": str(company_id)})
    assert res.status_code == 200
    next_fy_id = res.json()["data"]["next_fy_id"] if "next_fy_id" in res.json()["data"] else None

    # In my current service implementation, it returns the closed FY.
    # Let's find the newly created FY.
    from app.modules.companies.models import FinancialYear
    from sqlalchemy import select
    stmt = select(FinancialYear).where(FinancialYear.previous_fy_id == fy_id)
    res_fy = await db.execute(stmt)
    next_fy = res_fy.scalar_one()

    # 3. Verify Balances in Next FY
    from app.modules.companies.models import FinancialYearOpeningBalance

    # Party (Asset) should be 400 DEBIT
    stmt = select(FinancialYearOpeningBalance).where(FinancialYearOpeningBalance.financial_year_id == next_fy.id, FinancialYearOpeningBalance.ledger_id == party_ledger_id)
    res_bal = await db.execute(stmt)
    bal = res_bal.scalar_one()
    assert bal.opening_balance == 400.0
    assert bal.balance_type == "DEBIT"

    # Sales (Income) should be 0
    stmt = select(FinancialYearOpeningBalance).where(FinancialYearOpeningBalance.financial_year_id == next_fy.id, FinancialYearOpeningBalance.ledger_id == sales_ledger_id)
    res_bal = await db.execute(stmt)
    bal = res_bal.scalar_one()
    assert bal.opening_balance == 0.0

    # Capital (Liability) should have profit of 400 (CREDIT)
    # Net Profit = 400. Capital += 400 (Cr).
    stmt = select(FinancialYearOpeningBalance).where(FinancialYearOpeningBalance.financial_year_id == next_fy.id, FinancialYearOpeningBalance.ledger_id == cap_ledger_id)
    res_bal = await db.execute(stmt)
    bal = res_bal.scalar_one()
    # If starting at 0, should be 400 CREDIT
    assert bal.opening_balance == 400.0
    assert bal.balance_type == "CREDIT"
