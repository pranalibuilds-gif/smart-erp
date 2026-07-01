import asyncio
import uuid
import random
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Settings from .env
DATABASE_URL = "postgresql+asyncpg://postgres:pranali25@localhost:5432/smarterp"

from app.modules.auth.models import User
from app.modules.companies.models import Company, FinancialYear
from app.modules.masters.models import Ledger, AccountGroup, StockItem, Warehouse, StockBalance
from app.modules.vouchers.models import Voucher, VoucherEntry
from app.shared.constants.business import VoucherType, VoucherStatus, BalanceType

async def stress_test(num_vouchers=100):
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Find a company
        res = await session.execute(select(Company).limit(1))
        company = res.scalar_one_or_none()
        if not company:
            print("No company found. Run seeds first.")
            return

        res = await session.execute(select(FinancialYear).where(FinancialYear.company_id == company.id).limit(1))
        fy = res.scalar_one()

        # Find ledgers
        res = await session.execute(select(Ledger).where(Ledger.company_id == company.id))
        ledgers = res.scalars().all()

        if len(ledgers) < 2:
            print("Not enough ledgers. Seeding basic ones...")
            # Create required groups if missing
            res = await session.execute(select(AccountGroup).where(AccountGroup.company_id == company.id, AccountGroup.name == "Current Assets"))
            grp = res.scalar_one_or_none()
            if not grp:
                 grp = AccountGroup(company_id=company.id, name="Current Assets", nature="ASSET", is_primary=True)
                 session.add(grp)
                 await session.flush()

            l1 = Ledger(company_id=company.id, group_id=grp.id, name="Inventory", opening_balance=0)
            l2 = Ledger(company_id=company.id, group_id=grp.id, name="Cash", opening_balance=100000)
            session.add_all([l1, l2])
            await session.commit()
            ledgers = [l1, l2]

        print(f"Generating {num_vouchers} vouchers for {company.name}...")
        prefix = str(uuid.uuid4())[:4].upper()

        for i in range(num_vouchers):
            l1, l2 = random.sample(ledgers, 2)
            amount = Decimal(random.randint(10, 1000))

            v = Voucher(
                company_id=company.id,
                financial_year_id=fy.id,
                voucher_type=VoucherType.JOURNAL,
                voucher_number=f"STR-{prefix}-{i:05d}",
                voucher_date=date.today(),
                status=VoucherStatus.POSTED,
                narration="Stress test voucher"
            )
            session.add(v)
            await session.flush()

            e1 = VoucherEntry(voucher_id=v.id, ledger_id=l1.id, debit_amount=amount, credit_amount=0)
            e2 = VoucherEntry(voucher_id=v.id, ledger_id=l2.id, debit_amount=0, credit_amount=amount)
            session.add_all([e1, e2])

            # Update ledger balances (manually for speed in stress test, bypassing service)
            l1.current_balance = Decimal(str(l1.current_balance)) + amount
            l2.current_balance = Decimal(str(l2.current_balance)) - amount

        await session.commit()
        print("Done.")

from sqlalchemy import select
import sys
if __name__ == "__main__":
    count = 200
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    asyncio.run(stress_test(count))
