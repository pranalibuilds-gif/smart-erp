import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_group_balances(db: AsyncSession, company_id: uuid.UUID, fy_id: uuid.UUID):
    # This query sums up ledger balances grouped by their account groups
    query = text("""
        SELECT
            ag.name as group_name,
            ag.nature,
            COALESCE(SUM(l.opening_balance * CASE WHEN l.opening_balance_type = 'CREDIT' THEN -1 ELSE 1 END), 0) +
            COALESCE(SUM(ve.debit_amount - ve.credit_amount), 0) as balance
        FROM account_groups ag
        JOIN ledgers l ON ag.id = l.group_id
        LEFT JOIN voucher_entries ve ON l.id = ve.ledger_id
        LEFT JOIN vouchers v ON v.id = ve.voucher_id AND v.status = 'POSTED' AND v.financial_year_id = :fy_id
        WHERE ag.company_id = :company_id
        GROUP BY ag.id, ag.name, ag.nature
    """)

    result = await db.execute(query, {"company_id": company_id, "fy_id": fy_id})
    return result.fetchall()
