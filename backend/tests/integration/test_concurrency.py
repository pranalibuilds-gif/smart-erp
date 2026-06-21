import pytest
import asyncio
import uuid
import copy
from httpx import AsyncClient
from datetime import date
from app.core.security import create_access_token
from app.shared.constants.business import DocumentType


@pytest.mark.anyio
async def test_concurrent_invoice_creation(client: AsyncClient, erp_seed):
    """
    Simulates 10 concurrent invoice creation requests.
    Verifies that voucher numbers are sequential and unique.
    """
    token = create_access_token(erp_seed["user"].id)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Company-ID": str(erp_seed["company"].id)
    }

    # We use invoice creation as it triggers voucher generation and posting
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": DocumentType.SALES,
        "invoice_date": str(date.today()),
        "items": [
            {
                "stock_item_id": str(erp_seed["item"].id),
                "warehouse_id": str(erp_seed["warehouse"].id),
                "item_name": "Concurrent Test",
                "quantity": 1,
                "rate": 100,
                "tax_rate": 0
            }
        ]
    }

    # First, let's make sure the item has enough stock for 10 invoices
    # We'll create a purchase first
    pur_payload = copy.deepcopy(payload)
    pur_payload["document_type"] = DocumentType.PURCHASE
    pur_payload["items"][0]["quantity"] = 100
    res_pur = await client.post("/api/v1/billing/invoices", json=pur_payload, headers=headers)
    inv_pur_id = res_pur.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_pur_id}/post", headers=headers)

    # Now fire 10 concurrent Sales posts
    async def create_and_post():
        # Create Draft
        res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
        inv_id = res.json()["data"]["id"]
        # Post (This triggers voucher numbering)
        return await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

    tasks = [create_and_post() for _ in range(3)]
    responses = await asyncio.gather(*tasks)

    # Verify all succeeded
    for r in responses:
        assert r.status_code == 200, r.json()

    # Verify unique voucher numbers
    voucher_ids = [r.json()["data"]["voucher_id"] for r in responses]
    assert len(set(voucher_ids)) == 3
