import pytest
import uuid
from datetime import date
from httpx import AsyncClient
from app.shared.constants.business import VoucherType, VoucherStatus, BalanceType
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import AccountGroup, Ledger, StockItem, Unit
from app.modules.auth.models import User, Role, UserCompanyRole
from app.core.security import create_access_token, hash_password

@pytest.fixture
async def voucher_seed(db):
    # Setup company, user, ledgers, items
    uid = str(uuid.uuid4())[:8]
    company = Company(name=f"Voucher Co {uid}", legal_name="Voucher Ltd", slug=f"v-co-{uid}")
    db.add(company)

    user = User(
        email=f"v-user-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="Voucher User",
        is_active=True
    )
    db.add(user)
    await db.flush()

    fy = FinancialYear(
        company_id=company.id,
        name="2025-2026",
        start_date=date(2025, 4, 1),
        end_date=date(2026, 3, 31)
    )
    db.add(fy)

    # Groups
    assets = AccountGroup(company_id=company.id, name="Assets", nature="ASSET", is_primary=True)
    income = AccountGroup(company_id=company.id, name="Income", nature="INCOME", is_primary=True)
    db.add(assets)
    db.add(income)
    await db.flush()

    # Ledgers
    cash = Ledger(company_id=company.id, group_id=assets.id, name="Cash", opening_balance=0, opening_balance_type=BalanceType.DEBIT)
    sales = Ledger(company_id=company.id, group_id=income.id, name="Sales", opening_balance=0, opening_balance_type=BalanceType.CREDIT)
    db.add(cash)
    db.add(sales)

    # Inventory items
    unit = Unit(company_id=company.id, name="PCS")
    db.add(unit)
    await db.flush()

    item = StockItem(company_id=company.id, unit_id=unit.id, name="Phone", current_quantity=10, average_cost=1000)
    db.add(item)

    # Assign User to Company
    role = Role(name=f"Role-{uid}")
    db.add(role)
    await db.flush()
    ucr = UserCompanyRole(user_id=user.id, company_id=company.id, role_id=role.id)
    db.add(ucr)

    await db.commit()
    return {
        "user": user,
        "company": company,
        "fy": fy,
        "cash": cash,
        "sales": sales,
        "item": item
    }

@pytest.mark.anyio
async def test_voucher_dr_cr_validation(client: AsyncClient, voucher_seed, db):
    token = create_access_token(voucher_seed["user"].id)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Company-ID": str(voucher_seed["company"].id)
    }

    payload = {
        "voucher_type": VoucherType.SALES,
        "voucher_date": str(date.today()),
        "narration": "Test sales",
        "entries": [
            {"ledger_id": str(voucher_seed["cash"].id), "debit_amount": 1000, "credit_amount": 0},
            {"ledger_id": str(voucher_seed["sales"].id), "debit_amount": 0, "credit_amount": 900}, # UNBALANCED
        ]
    }

    response = await client.post("/api/v1/vouchers", json=payload, headers=headers)
    assert response.status_code == 201
    voucher_id = response.json()["data"]["id"]

    response = await client.post(f"/api/v1/vouchers/{voucher_id}/post", headers=headers)
    assert response.status_code == 400
    assert "not balanced" in response.json()["message"]

@pytest.mark.anyio
async def test_negative_stock_rejection(client: AsyncClient, voucher_seed, db):
    token = create_access_token(voucher_seed["user"].id)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Company-ID": str(voucher_seed["company"].id)
    }

    payload = {
        "voucher_type": VoucherType.SALES,
        "entries": [
            {"ledger_id": str(voucher_seed["cash"].id), "debit_amount": 15000, "credit_amount": 0},
            {"ledger_id": str(voucher_seed["sales"].id), "debit_amount": 0, "credit_amount": 15000},
        ],
        "inventory_entries": [
            {"stock_item_id": str(voucher_seed["item"].id), "quantity": 15, "rate": 1000}
        ]
    }

    response = await client.post("/api/v1/vouchers", json=payload, headers=headers)
    assert response.status_code == 201
    voucher_id = response.json()["data"]["id"]

    response = await client.post(f"/api/v1/vouchers/{voucher_id}/post", headers=headers)
    assert response.status_code == 400
    assert "Negative stock not allowed" in response.json()["message"]

@pytest.mark.anyio
async def test_successful_posting_flow(client: AsyncClient, voucher_seed, db):
    token = create_access_token(voucher_seed["user"].id)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Company-ID": str(voucher_seed["company"].id)
    }

    payload = {
        "voucher_type": VoucherType.PURCHASE,
        "entries": [
            {"ledger_id": str(voucher_seed["cash"].id), "debit_amount": 0, "credit_amount": 6000},
            {"ledger_id": str(voucher_seed["sales"].id), "debit_amount": 6000, "credit_amount": 0},
        ],
        "inventory_entries": [
            {"stock_item_id": str(voucher_seed["item"].id), "quantity": 5, "rate": 1200}
        ]
    }

    response = await client.post("/api/v1/vouchers", json=payload, headers=headers)
    voucher_id = response.json()["data"]["id"]
    post_res = await client.post(f"/api/v1/vouchers/{voucher_id}/post", headers=headers)
    assert post_res.status_code == 200

    from app.modules.masters.models import Ledger
    from sqlalchemy import select
    res = await db.execute(select(Ledger).where(Ledger.id == voucher_seed["cash"].id))
    cash_ledger = res.scalar_one()
    assert float(cash_ledger.current_balance) == -6000.0

    res = await db.execute(select(StockItem).where(StockItem.id == voucher_seed["item"].id))
    item = res.scalar_one()
    assert float(item.current_quantity) == 15.0
    assert round(float(item.average_cost), 2) == 1066.67

    await client.post(f"/api/v1/vouchers/{voucher_id}/cancel", headers=headers)

    await db.refresh(cash_ledger)
    await db.refresh(item)

    assert float(cash_ledger.current_balance) == 0.0
    assert float(item.current_quantity) == 10.0
    assert float(item.average_cost) == 1000.0
