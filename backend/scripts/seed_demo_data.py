import asyncio
import uuid
import random
import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select, and_, delete

from app.core.config import settings
from app.core.security import hash_password
from app.modules.auth.models import User, Role, UserCompanyRole
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import AccountGroup, Ledger, StockItem, Unit, Warehouse
from app.modules.parties.models import Party
from app.modules.vouchers.models import Voucher
from app.modules.billing.models import Invoice, InvoiceItem
from app.modules.billing.service import InvoiceService
from app.modules.companies.fy_service import FinancialYearService
from app.modules.masters.seeds import seed_company_defaults
from app.shared.constants.business import DocumentType, InvoiceStatus, VoucherStatus
from app.modules.billing.schemas.invoices import InvoiceCreate

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Demo Constants
DEMO_EMAIL = "demo@smarterp.io"
DEMO_PASSWORD = "Password123"
COMPANY_NAME = "Nexus Industrial Solutions"
START_YEAR = 2019
CURRENT_YEAR = 2026

async def seed_demo():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        logger.info("--- Starting Demo Data Seeding (6+ Year History) ---")

        # 1. Check/Create Demo User
        res_user = await db.execute(select(User).where(User.email == DEMO_EMAIL))
        user = res_user.scalar_one_or_none()
        if not user:
            user = User(
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                full_name="Demo Administrator",
                is_active=True
            )
            db.add(user)
            await db.flush()
            logger.info(f"User {DEMO_EMAIL} created.")
        else:
            logger.info(f"User {DEMO_EMAIL} already exists.")

        # 2. Check/Create Company
        res_comp = await db.execute(select(Company).where(Company.slug == "nexus-demo"))
        company = res_comp.scalar_one_or_none()
        if not company:
            company = Company(
                name=COMPANY_NAME,
                legal_name=f"{COMPANY_NAME} Pvt Ltd",
                slug="nexus-demo",
                address="Plot 42, Industrial Area Phase II",
                state="Maharashtra",
                gst_number="27AAACN1234A1Z1"
            )
            db.add(company)
            await db.flush()

            # Setup RBAC
            res_role = await db.execute(select(Role).where(Role.name == "ADMIN"))
            admin_role = res_role.scalar_one_or_none()
            if not admin_role:
                admin_role = Role(name="ADMIN", description="Administrator")
                db.add(admin_role)
                await db.flush()

            db.add(UserCompanyRole(user_id=user.id, company_id=company.id, role_id=admin_role.id, is_owner=True))
            await seed_company_defaults(db, company.id, user.id)
            await db.commit()
            logger.info(f"Company {COMPANY_NAME} created and defaults seeded.")
        else:
            logger.info(f"Company {COMPANY_NAME} already exists. Continuing from current state.")

        # 3. Setup Masters
        res_unit = await db.execute(select(Unit).where(and_(Unit.name == "PCS", Unit.company_id == company.id)))
        unit_pcs = res_unit.scalar_one()

        # Get or create items
        items = []
        item_names = ["Steel Beam L-50", "Industrial Motor 5HP", "Copper Coil 100m", "Control Panel X1", "LED Floodlight 200W"]
        for name in item_names:
            res_item = await db.execute(select(StockItem).where(and_(StockItem.name == name, StockItem.company_id == company.id)))
            item = res_item.scalar_one_or_none()
            if not item:
                item = StockItem(company_id=company.id, unit_id=unit_pcs.id, name=name, current_quantity=0, average_cost=0)
                db.add(item)
            items.append(item)

        # Get or create parties
        parties = []
        party_names = ["Apex Constructions", "Global Manufacturing Co", "Precision Tools Ltd", "Horizon Logistics", "Metro Suppliers"]
        res_grp = await db.execute(select(AccountGroup).where(and_(AccountGroup.name == "Sundry Debtors", AccountGroup.company_id == company.id)))
        debtors_group = res_grp.scalar_one()

        for name in party_names:
            res_party = await db.execute(select(Party).where(and_(Party.name == name, Party.company_id == company.id)))
            party = res_party.scalar_one_or_none()
            if not party:
                p_ledger = Ledger(company_id=company.id, group_id=debtors_group.id, name=name)
                db.add(p_ledger)
                await db.flush()
                party = Party(company_id=company.id, ledger_id=p_ledger.id, name=name, is_customer=True)
                db.add(party)
            parties.append(party)

        res_wh = await db.execute(select(Warehouse).where(Warehouse.company_id == company.id))
        warehouse = res_wh.scalar_one()

        await db.commit()

        # 4. Historical Data Loop
        inv_service = InvoiceService(db)
        fy_service = FinancialYearService(db)

        for year in range(START_YEAR, CURRENT_YEAR + 1):
            fy_name = f"{year}-{year+1}"

            res_fy = await db.execute(select(FinancialYear).where(and_(FinancialYear.company_id == company.id, FinancialYear.name == fy_name)))
            fy = res_fy.scalar_one_or_none()

            if not fy:
                if year == START_YEAR:
                    logger.error(f"FY {fy_name} not found but expected as start year.")
                    return
                continue

            if fy.is_closed:
                logger.info(f"FY {fy_name} is already closed. Skipping transactions.")
                continue

            logger.info(f"FY {fy_name}: Generating transactions...")

            # Month range
            for month_offset in range(12):
                m = (fy.start_date.month + month_offset - 1) % 12 + 1
                y = year if m >= 4 else year + 1

                # Transactions
                for _ in range(random.randint(5, 10)):
                    is_purchase = random.random() < 0.3
                    doc_type = DocumentType.PURCHASE if is_purchase else DocumentType.SALES
                    target_item = random.choice(items)

                    qty = random.randint(100, 200) if is_purchase else random.randint(5, 20)
                    rate = random.randint(500, 1000) if is_purchase else random.randint(1500, 4000)

                    data = InvoiceCreate(
                        party_id=random.choice(parties).id,
                        document_type=doc_type,
                        invoice_date=date(y, m, random.randint(1, 28)),
                        items=[{"stock_item_id": target_item.id, "warehouse_id": warehouse.id, "item_name": target_item.name, "quantity": qty, "rate": rate, "tax_rate": 18}]
                    )

                    try:
                        inv = await inv_service.create_invoice(company.id, fy, user.id, data)
                        await inv_service.post_invoice(company.id, inv.id, user.id)
                    except Exception:
                        pass

            # HARDENING: Cleanup all DRAFT documents before closing
            await db.execute(delete(Invoice).where(and_(
                Invoice.company_id == company.id,
                Invoice.financial_year_id == fy.id,
                Invoice.status == InvoiceStatus.DRAFT
            )))
            await db.execute(delete(Voucher).where(and_(
                Voucher.company_id == company.id,
                Voucher.financial_year_id == fy.id,
                Voucher.status == VoucherStatus.DRAFT
            )))
            # Also stock adjustments if any (none created by seeder yet but good for safety)
            from app.modules.inventory.models import StockAdjustment
            await db.execute(delete(StockAdjustment).where(and_(
                StockAdjustment.company_id == company.id,
                StockAdjustment.financial_year_id == fy.id,
                StockAdjustment.status == InvoiceStatus.DRAFT
            )))

            await db.commit()

            # Close and Rollover (except current)
            if year < CURRENT_YEAR - 1:
                logger.info(f"FY {fy_name}: Closing year...")
                await fy_service.close_and_rollover(company.id, fy.id, user.id)
                await db.commit()

        logger.info("\n--- Demo Seeding Complete ---")
        logger.info(f"URL: http://localhost:3000")
        logger.info(f"User: {DEMO_EMAIL}")
        logger.info(f"Pass: {DEMO_PASSWORD}")

if __name__ == "__main__":
    asyncio.run(seed_demo())
