import pytest
import uuid
from datetime import date
from httpx import AsyncClient
from app.shared.constants.business import DocumentType, InvoiceStatus, VoucherStatus
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import AccountGroup, Ledger, StockItem, Unit, Warehouse
from app.modules.parties.models import Party
from app.core.security import create_access_token, hash_password
from app.modules.auth.models import User, Role, UserCompanyRole

@pytest.fixture
async def erp_seed(db):
    uid = str(uuid.uuid4())[:8]
    company = Company(name=f"ERP Co {uid}", legal_name="ERP Ltd", slug=f"erp-co-{uid}")
    db.add(company)

    user = User(
        email=f"erp-user-{uid}@example.com",
        hashed_password=hash_password("password123"),
        full_name="ERP User",
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

    # Required Groups
    assets = AccountGroup(company_id=company.id, name="Assets", nature="ASSET", is_primary=True)
    income = AccountGroup(company_id=company.id, name="Income", nature="INCOME", is_primary=True)
    expenses = AccountGroup(company_id=company.id, name="Expenses", nature="EXPENSE", is_primary=True)
    liabilities = AccountGroup(company_id=company.id, name="Liabilities", nature="LIABILITY", is_primary=True)
    db.add_all([assets, income, expenses, liabilities])
    await db.flush()

    # Subgroups
    curr_assets = AccountGroup(company_id=company.id, name="Current Assets", parent_id=assets.id)
    debtors = AccountGroup(company_id=company.id, name="Sundry Debtors", parent_id=curr_assets.id)
    creditors = AccountGroup(company_id=company.id, name="Sundry Creditors", parent_id=liabilities.id)
    db.add_all([curr_assets, debtors, creditors])
    await db.flush()

    # Required Ledgers
    sales_ledger = Ledger(company_id=company.id, group_id=income.id, name="Sales")
    pur_ledger = Ledger(company_id=company.id, group_id=expenses.id, name="Purchase")
    db.add_all([sales_ledger, pur_ledger])

    # Inventory items
    unit = Unit(company_id=company.id, name="PCS")
    db.add(unit)
    await db.flush()

    item = StockItem(company_id=company.id, unit_id=unit.id, name="Widget", current_quantity=0, average_cost=0)
    db.add(item)

    # Party
    # To create party we use service or manual
    p_ledger = Ledger(company_id=company.id, group_id=debtors.id, name="Test Client")
    db.add(p_ledger)
    await db.flush()
    party = Party(company_id=company.id, ledger_id=p_ledger.id, name="Test Client", is_customer=True)
    db.add(party)

    # Role
    role = Role(name=f"Admin-{uid}")
    db.add(role)
    await db.flush()
    db.add(UserCompanyRole(user_id=user.id, company_id=company.id, role_id=role.id))

    # Warehouse
    warehouse = Warehouse(company_id=company.id, name="Main", code="MAIN")
    db.add(warehouse)
    await db.flush()

    await db.commit()
    return {
        "user": user,
        "company": company,
        "fy": fy,
        "party": party,
        "item": item,
        "warehouse": warehouse,
        "sales_ledger": sales_ledger,
        "pur_ledger": pur_ledger
    }

@pytest.mark.anyio
async def test_complete_purchase_to_sale_flow(client: AsyncClient, erp_seed, db):
    token = create_access_token(erp_seed["user"].id)
    headers = {"Authorization": f"Bearer {token}", "X-Company-ID": str(erp_seed["company"].id)}

    # SCENARIO 1: Purchase 100 units @ 10
    payload = {
        "party_id": str(erp_seed["party"].id),
        "document_type": DocumentType.PURCHASE,
        "invoice_date": str(date.today()),
        "items": [
            {
                "stock_item_id": str(erp_seed["item"].id),
                "warehouse_id": str(erp_seed["warehouse"].id),
                "item_name": "Widget",
                "quantity": 100,
                "rate": 10,
                "tax_rate": 0
            }
        ]
    }

    # Create & Post Purchase
    res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
    assert res.status_code == 201
    inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

    # Verify Stock = 100, WAC = 10
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 100.0
    assert float(erp_seed["item"].average_cost) == 10.0

    # SCENARIO 2: Purchase 100 units @ 20
    payload["items"][0]["rate"] = 20
    res = await client.post("/api/v1/billing/invoices", json=payload, headers=headers)
    inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

    # Verify Stock = 200, WAC = 15
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 200.0
    assert float(erp_seed["item"].average_cost) == 15.0

    # SCENARIO 3: Sell 50 units
    payload_sale = {
        "party_id": str(erp_seed["party"].id),
        "document_type": DocumentType.SALES,
        "invoice_date": str(date.today()),
        "items": [
            {
                "stock_item_id": str(erp_seed["item"].id),
                "warehouse_id": str(erp_seed["warehouse"].id),
                "item_name": "Widget",
                "quantity": 50,
                "rate": 30, # Sale rate doesn't affect WAC
                "tax_rate": 0
            }
        ]
    }
    res = await client.post("/api/v1/billing/invoices", json=payload_sale, headers=headers)
    inv_id = res.json()["data"]["id"]
    await client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=headers)

    # Verify Stock = 150, WAC = 15
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 150.0
    assert float(erp_seed["item"].average_cost) == 15.0

    # SCENARIO 4: Cancel Sale
    await client.post(f"/api/v1/billing/invoices/{inv_id}/cancel", headers=headers)

    # Verify Stock = 200, WAC = 15
    await db.refresh(erp_seed["item"])
    assert float(erp_seed["item"].current_quantity) == 200.0
    assert float(erp_seed["item"].average_cost) == 15.0
