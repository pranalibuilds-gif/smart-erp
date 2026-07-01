import pytest
from httpx import AsyncClient
import uuid
from decimal import Decimal
from sqlalchemy import select, func, and_
from app.modules.vouchers.models import VoucherEntry, Voucher
from app.modules.masters.models import Ledger
from app.shared.constants.business import VoucherStatus

@pytest.mark.asyncio
async def test_ledger_balance_reconciliation(client: AsyncClient, accountant_token: str, erp_seed: dict, db):
    """Verify that Ledger.current_balance matches the sum of its voucher entries."""
    company_id = erp_seed["company"].id
    ledger_id = erp_seed["sales_ledger"].id

    # 1. Post a few vouchers affecting this ledger
    async def post_journal(amt):
        payload = {
            "voucher_type": "JOURNAL",
            "voucher_date": "2024-06-01",
            "entries": [
                {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": amt, "credit_amount": 0},
                {"ledger_id": str(ledger_id), "debit_amount": 0, "credit_amount": amt}
            ]
        }
        res = await client.post("/api/v1/vouchers", json=payload, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
        v_id = res.json()["data"]["id"]
        await client.post(f"/api/v1/vouchers/{v_id}/post", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})

    await post_journal(100)
    await post_journal(250)
    await post_journal(50)
    # Total Credit = 400. current_balance should be -400 (if starting at 0).

    # 2. Query cached balance
    # Important: expire_all to ensure we fetch fresh data from DB after client commits
    db.expire_all()
    stmt = select(Ledger).where(Ledger.id == ledger_id)
    res = await db.execute(stmt)
    ledger = res.scalar_one()
    cached_balance = Decimal(str(ledger.current_balance))

    # 3. Recompute from history
    # Only POSTED vouchers
    stmt = select(func.sum(VoucherEntry.debit_amount - VoucherEntry.credit_amount)).join(Voucher).where(
        and_(VoucherEntry.ledger_id == ledger_id, Voucher.status == VoucherStatus.POSTED)
    )
    res = await db.execute(stmt)
    computed_balance = res.scalar() or Decimal("0.00")

    assert cached_balance == computed_balance
    assert abs(cached_balance - Decimal("-400.00")) < Decimal("0.01")
