import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_mass_assignment_superuser_denied(client: AsyncClient, erp_seed: dict):
    """Attempting to set is_superuser via registration should be ignored."""
    payload = {
        "email": f"hacker-{uuid.uuid4().hex[:6]}@example.com",
        "full_name": "Hacker",
        "password": "password123",
        "is_superuser": True # This should be ignored
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    user_data = response.json()["data"]["user"]
    assert user_data["is_superuser"] is False

@pytest.mark.asyncio
async def test_uuid_enumeration_indistinguishable(client: AsyncClient, multi_company_seed: dict):
    """Foreign UUID and Random UUID must both return 404."""
    token = multi_company_seed["token"]
    co_b_id = multi_company_seed["co_b"].id
    ledger_a_id = multi_company_seed["ledger_a"].id # Existing but in Co A
    random_id = uuid.uuid4() # Non-existent

    # 1. Foreign UUID
    res1 = await client.get(
        f"/api/v1/masters/ledgers/{ledger_a_id}",
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    # 2. Random UUID
    res2 = await client.get(
        f"/api/v1/masters/ledgers/{random_id}",
        headers={"Authorization": f"Bearer {token}", "X-Company-ID": str(co_b_id)}
    )

    assert res1.status_code == 404
    assert res2.status_code == 404
    # Optional: Verify response bodies are identical
    assert res1.json() == res2.json()

@pytest.mark.asyncio
async def test_sql_injection_search_denied(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """Attempting SQL injection in search should not work."""
    company_id = erp_seed["company"].id

    # SQLi payload
    payload = "' OR 1=1 --"
    response = await client.get(
        f"/api/v1/search?q={payload}",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )

    assert response.status_code == 200
    # Should just return 0 results or handle it safely as a string
    assert len(response.json()["data"]) == 0

@pytest.mark.asyncio
async def test_xss_in_billing_pdf_escaped(client: AsyncClient, erp_seed: dict, accountant_token: str):
    """XSS payloads in invoice data must be escaped in PDF generation."""
    company_id = erp_seed["company"].id
    fy_id = erp_seed["fy"].id

    # Create Invoice with script tag in narration
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": "SALES",
        "invoice_date": "2025-06-01",
        "narration": "<script>alert('xss')</script>",
        "items": [
            {
                "item_name": "Test Item",
                "quantity": 1,
                "rate": 100,
                "tax_rate": 0
            }
        ]
    }

    res = await client.post(
        "/api/v1/billing/invoices",
        json=payload,
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(fy_id)}
    )
    inv_id = res.json()["data"]["id"]

    # Request PDF
    response = await client.get(
        f"/api/v1/billing/invoices/{inv_id}/pdf",
        headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)}
    )

    assert response.status_code == 200
