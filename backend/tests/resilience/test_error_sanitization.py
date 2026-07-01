import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_error_response_structure_sanitized(client: AsyncClient, accountant_token: str, erp_seed: dict):
    """Verify that error responses are consistent and don't leak internal details."""
    company_id = erp_seed["company"].id

    # 1. 404 Not Found
    res = await client.get(f"/api/v1/vouchers/{uuid.uuid4()}", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    data = res.json()
    assert res.status_code == 404
    assert data["success"] is False
    assert "message" in data
    # No stack traces or SQL mentioned
    assert "Traceback" not in str(data)
    assert "SELECT" not in str(data)

    # 2. 422 Validation Error
    res = await client.post("/api/v1/vouchers", json={"bad": "data"}, headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id)})
    data = res.json()
    assert res.status_code == 422
    assert data["success"] is False
    assert "data" in data # Pydantic error details

    # 3. 500 Internal Server Error (Simulated)
    from unittest.mock import patch
    with patch("app.modules.vouchers.router.VoucherService.list_vouchers", side_effect=Exception("Database Connection Timeout")):
        res = await client.get("/api/v1/vouchers", headers={"Authorization": f"Bearer {accountant_token}", "X-Company-ID": str(company_id), "X-Financial-Year-ID": str(erp_seed["fy"].id)})
        assert res.status_code == 500
        try:
            data = res.json()
            assert data["success"] is False
            assert data["message"] == "Internal server error"
            assert "Database" not in data["message"]
        except Exception:
            pytest.fail(f"500 Response was not JSON: {res.text}")
