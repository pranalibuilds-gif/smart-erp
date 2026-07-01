import asyncio
import uuid
import json
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Settings from .env
DATABASE_URL = "postgresql+asyncpg://postgres:pranali25@localhost:5432/smarterp"

from verification.scripts.audit_engine import AuditEngine
from app.modules.companies.models import Company, FinancialYear, CompanyInvitation
from app.modules.auth.models import User, Role, Permission
from app.modules.vouchers.models import Voucher, VoucherEntry, InventoryTransaction
from app.modules.masters.models import Ledger, AccountGroup, StockItem, Warehouse, StockBalance
from app.modules.parties.models import Party
from app.modules.billing.models import Invoice, InvoiceItem
from app.modules.inventory.models import StockAdjustment, StockAdjustmentItem, StockTransfer, StockTransferItem

async def run_audit():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Find a company
        res = await session.execute(select(Company).where(Company.name == "ABC Manufacturing Pvt Ltd"))
        company = res.scalar_one_or_none()

        if not company:
            res = await session.execute(select(Company).limit(1))
            company = res.scalar_one_or_none()

        if not company:
            print("No company found.")
            return

        res = await session.execute(select(FinancialYear).where(FinancialYear.company_id == company.id, FinancialYear.is_closed == False).order_by(FinancialYear.start_date.desc()).limit(1))
        fy = res.scalar_one_or_none()
        if not fy:
             res = await session.execute(select(FinancialYear).where(FinancialYear.company_id == company.id).order_by(FinancialYear.start_date.desc()).limit(1))
             fy = res.scalar_one()

        print(f"--- AUDIT REPORT FOR {company.name} (FY: {fy.name}) ---")

        audit = AuditEngine(session)

        print("\n[1] Ledger Balance Verification:")
        ledgers = await audit.audit_ledger_balances(company.id, fy.id)
        fails = [l for l in ledgers if l["status"] == "FAIL"]
        if not fails:
            print("  PASS: All ledger balances reconcile with transaction sums.")
        else:
            print(f"  FAIL: {len(fails)} ledgers drifted!")
            for f in fails:
                print(f"    - {f['name']}: Drift {f['drift']}")

        print("\n[2] Inventory Integrity:")
        inv = await audit.audit_inventory_integrity(company.id)
        inv_fails = [i for i in inv if i["status"] == "FAIL"]
        if not inv_fails:
            print("  PASS: Inventory balances reconcile across all warehouses.")
        else:
            print(f"  FAIL: {len(inv_fails)} items drifted!")
            for f in inv_fails:
                print(f"    - {f['name']}: Calculated {f['calculated_total']}, Cached {f['cached_total']}")
                for wh in f["warehouses"]:
                    if wh["status"] == "FAIL":
                        print(f"      * WH {wh['warehouse_id']}: Calc {wh['calculated']}, Cached {wh['cached']}, Drift {wh['calculated'] - wh['cached']}")

        print("\n[3] Financial Statement Reconciliation:")
        recon = await audit.audit_financial_statements(company.id, fy.id)
        if recon["reconciled"]:
            print("  PASS: P&L Net Profit matches Balance Sheet Earnings and Assets = Liab + Equity.")
        else:
            print("  FAIL: Statement mismatch!")
            print(f"    P&L Net Profit: {recon['p_l_net_profit']}")
            print(f"    BS Net Profit:  {recon['bs_net_profit']}")
            print(f"    Total Assets:   {recon['total_assets']}")
            print(f"    Total Liab+Eq:  {recon['total_liab_equity']}")
            print(f"    Drift:          {abs(recon['total_assets'] - recon['total_liab_equity'])}")

        print("\n[4] Database Consistency:")
        db_issues = await audit.audit_database_consistency()
        if not db_issues:
            print("  PASS: No orphan records or duplicates found.")
        else:
            for issue in db_issues:
                print(f"  ISSUE: {issue}")

if __name__ == "__main__":
    asyncio.run(run_audit())
