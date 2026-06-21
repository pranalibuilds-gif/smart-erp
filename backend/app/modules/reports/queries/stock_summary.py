import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_stock_summary_data(db: AsyncSession, company_id: uuid.UUID, fy_id: uuid.UUID):
    query = text("""
        SELECT
            si.id as item_id,
            si.name as item_name,
            COALESCE(fso_agg.opening_qty, 0) as opening_qty,
            COALESCE(fso_agg.opening_val / NULLIF(fso_agg.opening_qty, 0), si.average_cost) as opening_avg_cost,
            COALESCE(SUM(CASE WHEN it.direction = 1 THEN it.quantity ELSE 0 END), 0) as inward_qty,
            COALESCE(SUM(CASE WHEN it.direction = -1 THEN it.quantity ELSE 0 END), 0) as outward_qty
        FROM stock_items si
        LEFT JOIN (
            SELECT stock_item_id, SUM(quantity) as opening_qty, SUM(quantity * average_cost) as opening_val
            FROM fy_stock_openings
            WHERE financial_year_id = :fy_id
            GROUP BY stock_item_id
        ) fso_agg ON fso_agg.stock_item_id = si.id
        LEFT JOIN inventory_transactions it ON si.id = it.stock_item_id
        LEFT JOIN vouchers v ON v.id = it.voucher_id AND v.status = 'POSTED' AND v.financial_year_id = :fy_id
        WHERE si.company_id = :company_id
        GROUP BY si.id, si.name, si.average_cost, fso_agg.opening_qty, fso_agg.opening_val
    """)

    result = await db.execute(query, {"company_id": company_id, "fy_id": fy_id})
    return result.fetchall()
