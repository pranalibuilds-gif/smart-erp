import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_viewer_escalation_denied(client: AsyncClient, viewer_token: str, company_id: uuid.UUID):
    """Viewer should not be able to post vouchers."""
    # Attempt to post a voucher (even a non-existent one)
    v_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/vouchers/{v_id}/post",
        headers={"Authorization": f"Bearer {viewer_token}", "X-Company-ID": str(company_id)}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_accountant_team_management_denied(client: AsyncClient, accountant_token: str, company_id: uuid.UUID):
    """Accountant should not be able to invite users."""
    response = await client.post(
        f"/api/v1/companies/{company_id}/invite",
        json={"email": "hacker@evil.com", "role_id": str(uuid.uuid4())},
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_accountant_fy_close_denied(client: AsyncClient, accountant_token: str, company_id: uuid.UUID):
    """Accountant should not be able to close financial years."""
    fy_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/companies/{company_id}/financial-years/{fy_id}/close",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )
    assert response.status_code == 403
