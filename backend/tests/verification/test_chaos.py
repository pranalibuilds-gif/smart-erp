import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy import select, func
from app.modules.vouchers.models import Voucher
from app.modules.vouchers.service import InventoryPostingService

@pytest.mark.asyncio
async def test_fault_injection_during_voucher_post(client: AsyncClient, erp_seed: dict, admin_token: str, db):
    """
    Phase 7: Chaos & Fault Injection.
    Inject failure after inventory update but before voucher commit.
    Verify that inventory changes are rolled back.
    """
    headers = {"Authorization": f"Bearer {admin_token}", "X-Company-ID": str(erp_seed["company"].id)}

    # 1. Create a Draft Purchase (Increase Stock)
    payload = {
        "voucher_type": "PURCHASE",
        "entries": [
            {"ledger_id": str(erp_seed["pur_ledger"].id), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(erp_seed["cap_ledger"].id), "debit_amount": 0, "credit_amount": 100}
        ],
        "inventory_entries": [
            {"stock_item_id": str(erp_seed["item"].id), "warehouse_id": str(erp_seed["warehouse"].id), "quantity": 10, "rate": 10}
        ]
    }
    res = await client.post("/api/v1/vouchers", json=payload, headers=headers)
    v_id = res.json()["data"]["id"]

    # Capture initial qty
    await db.refresh(erp_seed["item"])
    initial_qty = float(erp_seed["item"].current_quantity)

    # 2. Post Voucher with Fault Injection
    # We patch search_service.update_index to fail (it's called at the end of post_voucher)
    with patch("app.modules.search.service.SearchService.update_index", side_effect=Exception("CHAOS FAILURE")):
        # Note: In our current implementation, search update is wrapped in try/except (soft-fail).
        # To test HARD failure, let's patch something critical like audit logging if it's NOT soft-fail,
        # or patch the database commit itself.

        with patch("sqlalchemy.ext.asyncio.AsyncSession.commit", side_effect=Exception("COMMIT FAILURE")):
            res = await client.post(f"/api/v1/vouchers/{v_id}/post", headers=headers)
            assert res.status_code == 500 # Internal Server Error

    # 3. VERIFY ROLLBACK
    # Quantity should NOT have changed
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == initial_qty

    # Voucher should NOT be POSTED
    res = await client.get(f"/api/v1/vouchers/{v_id}", headers=headers)
    assert res.json()["data"]["status"] == "DRAFT"
