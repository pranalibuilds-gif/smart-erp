import asyncio
from sqlalchemy import inspect
from app.shared.database.session import engine

async def audit_db():
    print("--- Database Integrity Inventory ---")
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda c: inspect(c).get_table_names())

        for table in tables:
            print(f"\nTable: {table}")

            # PK
            pk = await conn.run_sync(lambda c: inspect(c).get_pk_constraint(table))
            print(f"  PK: {pk.get('constrained_columns', [])}")

            # FKs
            fks = await conn.run_sync(lambda c: inspect(c).get_foreign_keys(table))
            for fk in fks:
                print(f"  FK: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']} (ondelete: {fk.get('options', {}).get('ondelete')})")

            # Unique Constraints
            uniques = await conn.run_sync(lambda c: inspect(c).get_unique_constraints(table))
            for u in uniques:
                print(f"  Unique: {u['column_names']}")

            # Indexes
            indexes = await conn.run_sync(lambda c: inspect(c).get_indexes(table))
            for idx in indexes:
                print(f"  Index: {idx['column_names']} (unique: {idx['unique']})")

if __name__ == "__main__":
    asyncio.run(audit_db())
