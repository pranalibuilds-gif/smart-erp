import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.modules.companies.models import Company
from app.shared.utils.integrity import IntegrityScanner

async def run_audit():
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as session:
        # Get all companies
        res = await session.execute(select(Company))
        companies = res.scalars().all()

        scanner = IntegrityScanner(session)
        total_errors = 0

        print("Starting Data Integrity Audit...")
        print("-" * 40)

        for co in companies:
            print(f"Auditing Company: {co.name}")

            l_errs = await scanner.scan_ledgers(co.id)
            v_errs = await scanner.scan_vouchers(co.id)
            i_errs = await scanner.scan_invoices(co.id)

            all_errs = l_errs + v_errs + i_errs
            if not all_errs:
                print("  [OK] No integrity issues found.")
            else:
                for e in all_errs:
                    print(f"  [ERROR] {e}")
                total_errors += len(all_errs)

        print("-" * 40)
        print(f"Audit Complete. Total Errors found: {total_errors}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_audit())
