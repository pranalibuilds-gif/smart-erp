import asyncio
import uuid
import random
import logging
import sys
from datetime import date, timedelta, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, delete

from app.core.config import settings
from app.modules.companies.service import CompanyService
from app.modules.companies.fy_service import FinancialYearService
from app.modules.auth.models import User, Role, UserCompanyRole
from app.modules.companies.models import Company, FinancialYear, FinancialYearOpeningBalance, FinancialYearStockOpening
from app.modules.masters.models import StockItem, Warehouse, StockBalance, Unit, Ledger, AccountGroup
from app.modules.vouchers.models import Voucher, VoucherEntry, InventoryTransaction, VoucherSequence
from app.modules.billing.models import Invoice, InvoiceItem
from app.modules.inventory.models import StockTransfer, StockAdjustment
from app.modules.parties.models import Party

from app.modules.masters.service import MastersService
from app.modules.parties.service import PartyService
from app.modules.billing.service import InvoiceService
from app.modules.banking.service import BankingService
from app.modules.vouchers.service import VoucherService

from app.modules.companies.schemas import CompanyCreate
from app.modules.masters.schemas.warehouses import WarehouseCreate
from app.modules.masters.schemas.stock_items import StockItemCreate
from app.modules.parties.schemas.parties import PartyCreate
from app.modules.billing.schemas.invoices import InvoiceCreate, InvoiceItemCreate
from app.modules.banking.schemas.banking import PaymentVoucherCreate, PaymentAllocationCreate
from app.shared.constants.business import DocumentType, VoucherType

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

COMPANY_NAME = "ABC Manufacturing Pvt Ltd"

async def generate_demo():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # --- WIPE ---
        res = await session.execute(select(Company).where(Company.name == COMPANY_NAME))
        for co in res.scalars().all():
            cid = co.id
            logger.info(f"Wiping existing {COMPANY_NAME} ({cid})...")
            await session.execute(delete(User).where(User.email.like("%@abcmfg.com")))
            # Standard wipe logic
            await session.execute(delete(FinancialYearOpeningBalance).where(FinancialYearOpeningBalance.ledger_id.in_(select(Ledger.id).where(Ledger.company_id == cid))))
            await session.execute(delete(FinancialYearStockOpening).where(FinancialYearStockOpening.financial_year_id.in_(select(FinancialYear.id).where(FinancialYear.company_id == cid))))
            await session.execute(delete(InventoryTransaction).where(InventoryTransaction.voucher_id.in_(select(Voucher.id).where(Voucher.company_id == cid))))
            await session.execute(delete(VoucherEntry).where(VoucherEntry.voucher_id.in_(select(Voucher.id).where(Voucher.company_id == cid))))
            await session.execute(delete(InvoiceItem).where(InvoiceItem.invoice_id.in_(select(Invoice.id).where(Invoice.company_id == cid))))
            await session.execute(delete(Invoice).where(Invoice.company_id == cid))
            await session.execute(delete(StockTransfer).where(StockTransfer.company_id == cid))
            await session.execute(delete(StockAdjustment).where(StockAdjustment.company_id == cid))
            await session.execute(delete(VoucherSequence).where(VoucherSequence.company_id == cid))
            await session.execute(delete(Voucher).where(Voucher.company_id == cid))
            await session.execute(delete(StockBalance).where(StockBalance.warehouse_id.in_(select(Warehouse.id).where(Warehouse.company_id == cid))))
            await session.execute(delete(Party).where(Party.company_id == cid))
            await session.execute(delete(Ledger).where(Ledger.company_id == cid))
            await session.execute(delete(StockItem).where(StockItem.company_id == cid))
            await session.execute(delete(Warehouse).where(Warehouse.company_id == cid))
            await session.execute(delete(AccountGroup).where(AccountGroup.company_id == cid))
            await session.execute(delete(Company).where(Company.id == cid))
        await session.commit()

        # --- SETUP ---
        res = await session.execute(select(User.id).where(User.email == "admin@smaterp.internal"))
        admin_id = res.scalar_one_or_none() or (await session.execute(select(User.id))).scalar()

        co_svc = CompanyService(session)
        logger.info(f"Creating company: {COMPANY_NAME}")
        company = await co_svc.create_company(admin_id, CompanyCreate(
            name=COMPANY_NAME, legal_name=f"{COMPANY_NAME} Pvt Ltd", email="contact@abcmfg.com", phone="912233445566",
            address="MIDC", state="Maharashtra", country="India", gst_number="27ABCDE1234F1Z5",
            financial_year_start=date(2021, 4, 1)
        ))
        company_id = company.id
        await session.commit()

        ms = MastersService(session)
        ps = PartyService(session)
        isvc = InvoiceService(session)
        bsvc = BankingService(session)
        fy_svc = FinancialYearService(session)

        wh_ids = [(await session.execute(select(Warehouse.id).where(and_(Warehouse.company_id == company_id, Warehouse.code == "MAIN")))).scalar_one()]
        for n, c in [("Finished Goods", "FGWH"), ("Raw Material", "RMWH")]:
            wh = await ms.create_warehouse(company_id, admin_id, WarehouseCreate(name=n, code=c))
            wh_ids.append(wh.id)

        unit_kg_id = (await session.execute(select(Unit.id).where(and_(Unit.company_id == company_id, Unit.name == "KG")))).scalar_one()
        item_ids = []
        for i in range(100):
            it = await ms.create_stock_item(company_id, admin_id, StockItemCreate(name=f"Product {i+1}", sku=f"SKU-{1000+i}", unit_id=unit_kg_id))
            item_ids.append(it.id)

        cust_info = []
        for i in range(50):
            p = await ps.create_party(company_id, admin_id, PartyCreate(name=f"Customer {i+1}", is_customer=True))
            cust_info.append((p.id, p.ledger_id))

        supp_info = []
        for i in range(20):
            p = await ps.create_party(company_id, admin_id, PartyCreate(name=f"Supplier {i+1}", is_supplier=True))
            supp_info.append((p.id, p.ledger_id))
        await session.commit()

        bank_id = (await session.execute(select(Ledger.id).where(and_(Ledger.company_id == company_id, Ledger.name == "Bank")))).scalar_one()

        # --- SIMULATION ---
        for yr in range(6):
            # Always re-fetch FY to avoid detached issues
            res_fy = await session.execute(select(FinancialYear).where(FinancialYear.company_id == company_id).order_by(FinancialYear.start_date))
            all_fys = res_fy.scalars().all()
            if yr >= len(all_fys): break
            fy = all_fys[yr]
            fy_id = fy.id
            logger.info(f"Simulating {fy.name}...")

            # 1. Purchases (50 per year)
            for _ in range(50):
                sid, s_lid = random.choice(supp_info)
                try:
                    inv = await isvc.create_invoice(company_id, fy, admin_id, InvoiceCreate(
                        party_id=sid, document_type=DocumentType.PURCHASE,
                        invoice_date=fy.start_date + timedelta(days=random.randint(0, 30)),
                        items=[InvoiceItemCreate(stock_item_id=random.choice(item_ids), warehouse_id=random.choice(wh_ids), item_name="P", quantity=1000, rate=100)]
                    ))
                    await isvc.post_invoice(company_id, inv.id, admin_id)
                except Exception as e:
                    logger.debug(f"Purchase failed: {e}")
            await session.commit()

            # 2. Sales (150 per year)
            for _ in range(150):
                cid, c_lid = random.choice(cust_info)
                txn_date = fy.start_date + timedelta(days=random.randint(31, 350))
                if txn_date > date.today(): txn_date = date.today()
                try:
                    inv = await isvc.create_invoice(company_id, fy, admin_id, InvoiceCreate(
                        party_id=cid, document_type=DocumentType.SALES,
                        invoice_date=txn_date,
                        items=[InvoiceItemCreate(stock_item_id=random.choice(item_ids), warehouse_id=random.choice(wh_ids), item_name="S", quantity=10, rate=250)]
                    ))
                    await isvc.post_invoice(company_id, inv.id, admin_id)
                    # 80% Payment
                    if random.random() < 0.8:
                        await bsvc.create_payment_or_receipt(company_id, fy, admin_id, PaymentVoucherCreate(
                            bank_cash_ledger_id=bank_id, party_ledger_id=c_lid, amount=float(inv.total_amount),
                            voucher_date=txn_date + timedelta(days=5),
                            allocations=[PaymentAllocationCreate(invoice_id=inv.id, allocated_amount=float(inv.total_amount))]
                        ), is_receipt=True)
                except Exception as e:
                    logger.debug(f"Sale failed: {e}")
            await session.commit()

            if yr < 5:
                logger.info(f"Closing {fy.name}...")
                # Draft cleanup
                await session.execute(delete(Voucher).where(and_(Voucher.financial_year_id == fy_id, Voucher.status == "DRAFT")))
                await session.execute(delete(Invoice).where(and_(Invoice.financial_year_id == fy_id, Invoice.status == "DRAFT")))
                await session.commit()
                await fy_svc.close_and_rollover(company_id, fy_id, admin_id)
                await session.commit()

    logger.info("Demo Data Generation Finished.")

if __name__ == "__main__":
    asyncio.run(generate_demo())
