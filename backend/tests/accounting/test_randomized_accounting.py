import pytest
from httpx import AsyncClient
import uuid
import random
from decimal import Decimal
from sqlalchemy import select, func
from app.modules.masters.models import Ledger

@pytest.mark.asyncio
async def test_trial_balance_always_zeros(client: AsyncClient, accountant_token: str, erp_seed: dict, db):
    """Generate multiple random journals and verify that Trial Balance sum is always zero."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # Get 4 random ledgers from the seed
    stmt = select(Ledger).where(Ledger.company_id == company_id).limit(4)
    res = await db.execute(stmt)
    ledgers = res.scalars().all()
    ledger_ids = [l.id for l in ledgers]

    for _ in range(5): # 5 random transactions
        amt = random.randint(10, 1000)
        # Select 2 distinct ledgers
        l_dr, l_cr = random.sample(ledger_ids, 2)

        payload = {
            "voucher_type": "JOURNAL",
            "voucher_date": "2024-06-01",
            "entries": [
                {"ledger_id": str(l_dr), "debit_amount": amt, "credit_amount": 0},
                {"ledger_id": str(l_cr), "debit_amount": 0, "credit_amount": amt}
            ]
        }
        res = await client.post("/api/v1/vouchers", json=payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
        v_id = res.json()["data"]["id"]
        await client.post(f"/api/v1/vouchers/{v_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    # Verify Trial Balance
    db.expire_all()
    stmt = select(func.sum(Ledger.current_balance)).where(Ledger.company_id == company_id)
    res = await db.execute(stmt)
    total_balance = res.scalar() or Decimal("0.00")

    # Due to double entry, sum of all balances (Dr - Cr) must be 0
    assert abs(total_balance) < Decimal("0.01")
