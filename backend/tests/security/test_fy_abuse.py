import pytest
from httpx import AsyncClient
import uuid
from sqlalchemy import update
from app.modules.companies.models import FinancialYear

@pytest.mark.asyncio
async def test_post_into_closed_fy_rejected(client: AsyncClient, accountant_token: str, erp_seed: dict, db):
    """Attempting to post a voucher into a closed FY must be rejected."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # Force close the FY in DB
    await db.execute(update(FinancialYear).where(FinancialYear.id == fy_id).values(is_closed=True))
    await db.commit()

    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [
            {"ledger_id": str(uuid.uuid4()), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(uuid.uuid4()), "debit_amount": 0, "credit_amount": 100}
        ]
    }

    response = await client.post(
        "/api/v1/vouchers",
        json=voucher_data,
        headers={
            "Authorization": f"Bearer {accountant_token}",
            "X-Company-ID": str(company_id),
            "X-Financial-Year-ID": str(fy_id)
        }
    )
    # The service layer checks if FY is closed before creation/posting
    assert response.status_code == 400
    assert "closed" in response.json()["message"].lower()
