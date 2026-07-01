import asyncio
import random
import sys
import os
import uuid
from datetime import date, timedelta, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, and_

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import hash_password
from app.modules.auth.models import User, Role, Permission, UserCompanyRole
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import AccountGroup, Ledger, StockItem, Unit, Warehouse
from app.modules.parties.models import Party
from app.modules.vouchers.service import VoucherService, InventoryPostingService
from app.modules.billing.service import InvoiceService
from app.modules.banking.service import BankingService
from app.modules.companies.fy_service import FinancialYearService
from app.shared.constants.business import VoucherType, DocumentType, AccountNature, LedgerType
from app.shared.constants.permissions import ALL_PERMISSIONS

async def create_companies(session: AsyncSession, user_id: uuid.UUID):
    profiles = [
        {"name": "Alpha Wholesale", "type": "WHOLESALE"},
        {"name": "Beta Manufacturing", "type": "MANUFACTURING"},
        {"name": "Gamma IT Services", "type": "SERVICE"},
        {"name": "Delta Mega Retail", "type": "RETAIL"},
        {"name": "Omega Logistics", "type": "DISTRIBUTION"}
    ]

    companies = []
    from app.modules.companies.service import CompanyService
    co_service = CompanyService(session)
    from app.modules.companies.schemas import CompanyCreate

    for p in profiles:
        print(f"Creating Company: {p['name']}...")
        data = CompanyCreate(
            name=p["name"],
            legal_name=f"{p['name']} Pvt Ltd",
            financial_year_start=date(2025, 4, 1)
        )
        company = await co_service.create_company(user_id, data)
        companies.append(company)

    return companies

async def run_simulation():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        # 1. Create a master user with unique email
        uid = str(uuid.uuid4())[:6]
        print(f"Seeding Master User (sim-{uid})...")
        user = User(
            email=f"admin-{uid}@smarterp.sim",
            hashed_password=hash_password("admin123"),
            full_name=f"Simulation Admin {uid}",
            is_active=True
        )
        session.add(user)
        await session.flush()

        # 2. Create Companies
        companies = await create_companies(session, user.id)

        # 3. Simulate Activity per Company
        for co in companies:
            print(f"\n--- Simulating Business for {co.name} ---")

            # Fetch FY
            res = await session.execute(select(FinancialYear).where(FinancialYear.company_id == co.id))
            fy = res.scalar_one()

            # Services
            v_service = VoucherService(session)
            inv_service = InvoiceService(session)
            bank_service = BankingService(session)

            # Masters (Fetch seeded ones)
            res = await session.execute(select(Ledger).where(and_(Ledger.company_id == co.id, Ledger.name == "Sales")))
            sales_ledger = res.scalar_one()
            res = await session.execute(select(Ledger).where(and_(Ledger.company_id == co.id, Ledger.name == "Purchase")))
            pur_ledger = res.scalar_one()
            res = await session.execute(select(Ledger).where(and_(Ledger.company_id == co.id, Ledger.name == "Cash")))
            cash_ledger = res.scalar_one()

            # Create some Parties
            parties = []
            for i in range(10):
                p_ledger = Ledger(company_id=co.id, group_id=sales_ledger.group_id, name=f"Customer {i+1}")
                session.add(p_ledger)
                await session.flush()
                party = Party(company_id=co.id, ledger_id=p_ledger.id, name=f"Customer {i+1}", is_customer=True)
                session.add(party)
                parties.append(party)

            # Create some Stock Items
            items = []
            res = await session.execute(select(Unit).where(Unit.company_id == co.id))
            unit = res.scalars().first()
            res = await session.execute(select(Warehouse).where(Warehouse.company_id == co.id))
            warehouse = res.scalars().first()

            for i in range(20):
                item = StockItem(company_id=co.id, unit_id=unit.id, name=f"Product {i+1}", current_quantity=0, average_cost=0)
                session.add(item)
                items.append(item)
            await session.flush()

            # --- 12 Month Transaction Loop ---
            current_date = fy.start_date
            print(f"Starting 12-month transaction loop from {current_date}...")

            for m in range(12):
                month_name = (current_date + timedelta(days=m*30)).strftime("%B %Y")
                print(f"  > Simulating {month_name}...")

                # Each month: 5 Purchases, 15 Sales, 10 Payments
                for _ in range(5):
                    # Purchase
                    it = random.choice(items)
                    qty = random.randint(50, 100)
                    rate = random.randint(10, 50)
                    from app.modules.billing.schemas import InvoiceCreate, InvoiceItemCreate
                    data = InvoiceCreate(
                        party_id=parties[0].id, # Use first as supplier for simplicity
                        document_type=DocumentType.PURCHASE,
                        invoice_date=current_date + timedelta(days=random.randint(0, 28)),
                        items=[InvoiceItemCreate(item_name=it.name, stock_item_id=it.id, warehouse_id=warehouse.id, quantity=qty, rate=rate)]
                    )
                    inv = await inv_service.create_invoice(co.id, fy, user.id, data)
                    await inv_service.post_invoice(co.id, inv.id, user.id)

                for _ in range(15):
                    # Sale
                    it = random.choice(items)
                    if it.current_quantity < 5: continue
                    qty = random.randint(1, 5)
                    rate = random.randint(60, 100)
                    data = InvoiceCreate(
                        party_id=random.choice(parties).id,
                        document_type=DocumentType.SALES,
                        invoice_date=current_date + timedelta(days=random.randint(0, 28)),
                        items=[InvoiceItemCreate(item_name=it.name, stock_item_id=it.id, warehouse_id=warehouse.id, quantity=qty, rate=rate)]
                    )
                    try:
                        inv = await inv_service.create_invoice(co.id, fy, user.id, data)
                        await inv_service.post_invoice(co.id, inv.id, user.id)
                    except:
                        continue # Negative stock check might trigger if multiple sales hit same item

                # Increment date
                current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                await session.commit() # Commit month-by-month to avoid massive single transaction

            # 4. Year End Closing
            print(f"Closing Financial Year for {co.name}...")
            fy_service = FinancialYearService(session)
            await fy_service.close_and_rollover(co.id, fy.id, user.id)
            await session.commit()

        print("\nSimulation Complete.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_simulation())
