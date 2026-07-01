import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_unbalanced_voucher_rejected(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Vouchers where Debit != Credit must be rejected."""
    company_id = erp_seed["company"].id
    ledger_a = erp_seed["sales_ledger"].id
    ledger_b = erp_seed["pur_ledger"].id

    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [
            {"ledger_id": str(ledger_a), "debit_amount": 100, "credit_amount": 0},
            {"ledger_id": str(ledger_b), "debit_amount": 0, "credit_amount": 99}
        ]
    }

    response = await client.post(
        "/api/v1/vouchers",
        json=voucher_data,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    assert response.status_code == 400
    assert "balanced" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_single_entry_voucher_rejected(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Vouchers must have at least 2 entries."""
    company_id = erp_seed["company"].id
    ledger_id = erp_seed["sales_ledger"].id

    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [
            {"ledger_id": str(ledger_id), "debit_amount": 100, "credit_amount": 0}
        ]
    }

    response = await client.post(
        "/api/v1/vouchers",
        json=voucher_data,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    # This might be caught by Pydantic validation (422) or service (400)
    assert response.status_code in [400, 422]
