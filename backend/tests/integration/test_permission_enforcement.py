import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_viewer_denied_post_voucher(client: AsyncClient, viewer_token: str, company_id: uuid.UUID):
    """
    Scenario: User with VIEW permission tries to create a voucher.
    Expected: 403 Forbidden
    """
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
        headers={"Authorization": f"Bearer {viewer_token}", "X-Company-ID": str(company_id)}
    )

    assert response.status_code == 403
    assert "Permission denied: voucher:create required" in response.json()["message"]

@pytest.mark.asyncio
async def test_accountant_allowed_post_voucher(client: AsyncClient, accountant_token: str, company_id: uuid.UUID):
    """
    Scenario: User with CREATE permission tries to create a voucher.
    Expected: 201 Created (assuming masters exist, but here we just check permission gate)
    Note: This might fail with 404 if ledgers don't exist, but it should NOT be 403.
    """
    voucher_data = {
        "voucher_type": "JOURNAL",
        "voucher_date": "2024-06-01",
        "entries": [] # Intentionally invalid data to hit service layer after permission check
    }

    response = await client.post(
        "/api/v1/vouchers",
        json=voucher_data,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )

    # 422 because entries are empty, which means it passed the permission check!
    assert response.status_code != 403

@pytest.mark.asyncio
async def test_viewer_allowed_view_reports(client: AsyncClient, viewer_token: str, company_id: uuid.UUID):
    """
    Scenario: User with VIEW permission tries to fetch Trial Balance.
    Expected: 200 OK
    """
    response = await client.get(
        "/api/v1/reports/trial-balance",
        headers={"Authorization": f"Bearer {viewer_token}", "X-Company-ID": str(company_id)}
    )

    assert response.status_code == 200
