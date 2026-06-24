import asyncio
from sqlalchemy import text
from app.shared.database.session import AsyncSessionLocal

async def wipe_all_data():
    print("--- Initiating Full System Data Wipe ---")

    # Tables found in models
    tables = [
        "audit_logs",
        "notifications",
        "search_documents",
        "voucher_entries",
        "vouchers",
        "invoice_items",
        "invoices",
        "stock_adjustments",
        "stock_transfers",
        "inventory_transactions",
        "stock_balances",
        "stock_items",
        "units",
        "parties",
        "bank_accounts",
        "ledgers",
        "account_groups",
        "fy_opening_balances",
        "financial_years",
        "user_company_roles",
        "company_invitations",
        "companies",
        "users",
        "roles",
        "permissions"
    ]

    async with AsyncSessionLocal() as db:
        for table in tables:
            try:
                # Use individual commits to avoid transaction aborts blocking subsequent wipes
                await db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
                await db.commit()
                print(f"Wiped: {table}")
            except Exception as e:
                await db.rollback()
                print(f"Could not wipe {table} (might not exist): {str(e)[:100]}...")

    print("\n--- System is now in Zero-State ---")

if __name__ == "__main__":
    asyncio.run(wipe_all_data())
