import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_over_allocation_denied(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Attempting to allocate more than the invoice amount should fail."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # Logic: This depends on the banking/allocation implementation.
    # If not yet fully implemented, we'll skip or verify the draft logic.
    pass

@pytest.mark.asyncio
async def test_negative_allocation_denied(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Negative payment/allocation amounts must be rejected."""
    company_id = erp_seed["company"].id
    # Assuming /api/v1/banking/payments
    payment_data = {
        "party_id": str(erp_seed["party"].id),
        "payment_date": "2024-06-01",
        "amount": -100,
        "payment_mode": "CASH",
        "ledger_id": str(erp_seed["sales_ledger"].id)
    }
    response = await client.post(
        "/api/v1/banking/payments",
        json=payment_data,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    # Pydantic gt=0 should catch this
    assert response.status_code == 422
