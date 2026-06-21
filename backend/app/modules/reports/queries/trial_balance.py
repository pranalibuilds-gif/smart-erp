import uuid
from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.masters.models import Ledger
from app.modules.vouchers.models import Voucher, VoucherEntry
from app.shared.constants.business import VoucherStatus, BalanceType


async def get_trial_balance_data(db: AsyncSession, company_id: uuid.UUID, fy_id: uuid.UUID):
    # CTE for summing up posted voucher entries
    stmt = (
        select(
            Ledger.id.label("ledger_id"),
            Ledger.name.label("ledger_name"),
            Ledger.opening_balance.label("opening_bal"),
            Ledger.opening_balance_type.label("opening_type"),
            func.coalesce(func.sum(VoucherEntry.debit_amount), 0).label("debit_total"),
            func.coalesce(func.sum(VoucherEntry.credit_amount), 0).label("credit_total")
        )
        .join(VoucherEntry, Ledger.id == VoucherEntry.ledger_id, isouter=True)
        .join(Voucher, Voucher.id == VoucherEntry.voucher_id, isouter=True)
        .where(Ledger.company_id == company_id)
        # Only include posted vouchers in this FY
        .where(
            and_(
                or_(Voucher.status == VoucherStatus.POSTED, Voucher.status == None),
                or_(Voucher.financial_year_id == fy_id, Voucher.financial_year_id == None)
            )
        )
        .group_by(Ledger.id, Ledger.name, Ledger.opening_balance, Ledger.opening_balance_type)
    )

    # Wait, the above logic for filtering vouchers might exclude ledgers with no entries.
    # Improved Query:
    query = text("""
        SELECT
            l.id as ledger_id,
            l.name as ledger_name,
            l.opening_balance,
            l.opening_balance_type,
            COALESCE(SUM(ve.debit_amount), 0) as debit_total,
            COALESCE(SUM(ve.credit_amount), 0) as credit_total
        FROM ledgers l
        LEFT JOIN voucher_entries ve ON l.id = ve.ledger_id
        LEFT JOIN vouchers v ON v.id = ve.voucher_id AND v.status = 'POSTED' AND v.financial_year_id = :fy_id
        WHERE l.company_id = :company_id
        GROUP BY l.id, l.name, l.opening_balance, l.opening_balance_type
    """)

    result = await db.execute(query, {"company_id": company_id, "fy_id": fy_id})
    return result.fetchall()
