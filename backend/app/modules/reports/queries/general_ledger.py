import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_ledger_entries(db: AsyncSession, company_id: uuid.UUID, fy_id: uuid.UUID, ledger_id: uuid.UUID):
    query = text("""
        SELECT
            v.voucher_date as date,
            v.voucher_number,
            v.voucher_type,
            ve.narration,
            ve.debit_amount as debit,
            ve.credit_amount as credit
        FROM voucher_entries ve
        JOIN vouchers v ON v.id = ve.voucher_id
        WHERE v.company_id = :company_id
          AND v.financial_year_id = :fy_id
          AND ve.ledger_id = :ledger_id
          AND v.status = 'POSTED'
        ORDER BY v.voucher_date ASC, v.created_at ASC
    """)

    result = await db.execute(query, {
        "company_id": company_id,
        "fy_id": fy_id,
        "ledger_id": ledger_id
    })
    return result.fetchall()
