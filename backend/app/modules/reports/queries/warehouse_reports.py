import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_warehouse_stock(db: AsyncSession, company_id: uuid.UUID, warehouse_id: uuid.UUID):
    query = text("""
        SELECT
            si.id as item_id,
            si.name as item_name,
            sb.quantity,
            sb.average_cost
        FROM stock_balances sb
        JOIN stock_items si ON si.id = sb.stock_item_id
        WHERE sb.warehouse_id = :warehouse_id AND si.company_id = :company_id
        ORDER BY si.name
    """)
    result = await db.execute(query, {"company_id": company_id, "warehouse_id": warehouse_id})
    return result.fetchall()


async def get_transfer_history(db: AsyncSession, company_id: uuid.UUID, fy_id: uuid.UUID):
    query = text("""
        SELECT
            st.id,
            st.transfer_no,
            st.transfer_date as date,
            fw.name as from_warehouse,
            tw.name as to_warehouse,
            (SELECT COUNT(*) FROM stock_transfer_items sti WHERE sti.transfer_id = st.id) as item_count,
            st.status
        FROM stock_transfers st
        JOIN warehouses fw ON fw.id = st.from_warehouse_id
        JOIN warehouses tw ON tw.id = st.to_warehouse_id
        WHERE st.company_id = :company_id AND st.financial_year_id = :fy_id
        ORDER BY st.transfer_date DESC
    """)
    result = await db.execute(query, {"company_id": company_id, "fy_id": fy_id})
    return result.fetchall()
