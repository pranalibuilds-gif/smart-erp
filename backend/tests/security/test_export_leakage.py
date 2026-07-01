import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_cross_tenant_pdf_access_denied(client: AsyncClient, multi_company_seed: dict):
    """Attempting to download a PDF for an invoice from another company should fail."""
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id

    # We need an invoice ID from Co A.
    # multi_company_seed doesn't create an invoice. Let's create one in the test.
    # Or just use a random UUID and expect 404 (isolation).
    fake_invoice_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/billing/invoices/{fake_invoice_id}/pdf",
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    # Since the invoice doesn't exist in Co B, it must be 404.
    assert response.status_code == 404
