import uuid
import asyncio
from decimal import Decimal
from typing import Dict, List, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import Ledger, StockItem, StockBalance
from app.modules.vouchers.models import Voucher, VoucherEntry, InventoryTransaction
from app.modules.companies.models import FinancialYear, FinancialYearOpeningBalance, FinancialYearStockOpening
from app.shared.constants.business import VoucherStatus, BalanceType


class AuditEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def audit_ledger_balances(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Stage 2: Ledger Balance Verification
        Calculates expected balance from Opening + Sum(VoucherEntries) and compares with cached balance.
        """
        # 1. Fetch all ledgers for the company
        stmt = select(Ledger).where(Ledger.company_id == company_id)
        res = await self.db.execute(stmt)
        ledgers = res.scalars().all()

        drift_report = []

        for ledger in ledgers:
            # 2. Get Opening Balance for this FY
            # Check FinancialYearOpeningBalance first, fallback to Ledger.opening_balance if it's the first year
            stmt_opening = select(FinancialYearOpeningBalance).where(
                and_(FinancialYearOpeningBalance.ledger_id == ledger.id, FinancialYearOpeningBalance.financial_year_id == fy_id)
            )
            res_opening = await self.db.execute(stmt_opening)
            fy_opening = res_opening.scalar_one_or_none()

            if fy_opening:
                opening = Decimal(str(fy_opening.opening_balance))
                if fy_opening.balance_type == BalanceType.CREDIT:
                    opening = -opening
            else:
                opening = Decimal(str(ledger.opening_balance))
                if ledger.opening_balance_type == BalanceType.CREDIT:
                    opening = -opening

            # 3. Sum all POSTED transactions for this ledger in this FY
            stmt_txns = select(
                func.sum(VoucherEntry.debit_amount).label("debit"),
                func.sum(VoucherEntry.credit_amount).label("credit")
            ).join(Voucher).where(
                and_(
                    VoucherEntry.ledger_id == ledger.id,
                    Voucher.company_id == company_id,
                    Voucher.financial_year_id == fy_id,
                    Voucher.status == VoucherStatus.POSTED
                )
            )
            res_txns = await self.db.execute(stmt_txns)
            txn_sums = res_txns.one()

            debit_sum = Decimal(str(txn_sums.debit or 0))
            credit_sum = Decimal(str(txn_sums.credit or 0))

            calculated_balance = opening + debit_sum - credit_sum
            cached_balance = Decimal(str(ledger.current_balance))

            drift = calculated_balance - cached_balance

            if abs(drift) > 0.001:
                drift_report.append({
                    "ledger_id": str(ledger.id),
                    "name": ledger.name,
                    "opening": float(opening),
                    "debits": float(debit_sum),
                    "credits": float(credit_sum),
                    "calculated": float(calculated_balance),
                    "cached": float(cached_balance),
                    "drift": float(drift),
                    "status": "FAIL"
                })
            else:
                drift_report.append({
                    "ledger_id": str(ledger.id),
                    "name": ledger.name,
                    "status": "PASS"
                })

        return drift_report

    async def audit_inventory_integrity(self, company_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Stage 3: Inventory Integrity
        Verifies Warehouse balances and Company aggregate balances.
        """
        stmt_items = select(StockItem).where(StockItem.company_id == company_id)
        res_items = await self.db.execute(stmt_items)
        items = res_items.scalars().all()

        report = []

        for item in items:
            # 1. Verify Aggregate (Company-wide)
            stmt_txns = select(
                func.sum(InventoryTransaction.quantity * InventoryTransaction.direction)
            ).join(Voucher).where(
                and_(
                    InventoryTransaction.stock_item_id == item.id,
                    Voucher.company_id == company_id,
                    Voucher.status == VoucherStatus.POSTED
                )
            )
            res_txns = await self.db.execute(stmt_txns)
            calculated_qty = Decimal(str(res_txns.scalar() or 0))
            cached_qty = Decimal(str(item.current_quantity))

            drift = calculated_qty - cached_qty

            item_status = "PASS" if abs(drift) < 0.001 else "FAIL"

            # 2. Verify per Warehouse
            stmt_balances = select(StockBalance).where(StockBalance.stock_item_id == item.id)
            res_balances = await self.db.execute(stmt_balances)
            wh_balances = res_balances.scalars().all()

            wh_details = []
            for bal in wh_balances:
                stmt_wh_txns = select(
                    func.sum(InventoryTransaction.quantity * InventoryTransaction.direction)
                ).join(Voucher).where(
                    and_(
                        InventoryTransaction.stock_item_id == item.id,
                        InventoryTransaction.warehouse_id == bal.warehouse_id,
                        Voucher.status == VoucherStatus.POSTED
                    )
                )
                res_wh_txns = await self.db.execute(stmt_wh_txns)
                calc_wh_qty = Decimal(str(res_wh_txns.scalar() or 0))
                cached_wh_qty = Decimal(str(bal.quantity))

                wh_drift = calc_wh_qty - cached_wh_qty
                wh_status = "PASS" if abs(wh_drift) < 0.001 else "FAIL"
                if wh_status == "FAIL": item_status = "FAIL"

                wh_details.append({
                    "warehouse_id": str(bal.warehouse_id),
                    "calculated": float(calc_wh_qty),
                    "cached": float(cached_wh_qty),
                    "status": wh_status
                })

            report.append({
                "item_id": str(item.id),
                "name": item.name,
                "calculated_total": float(calculated_qty),
                "cached_total": float(cached_qty),
                "status": item_status,
                "warehouses": wh_details
            })

        return report

    async def audit_financial_statements(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> Dict[str, Any]:
        """
        Stage 4: Financial Statement Reconciliation
        Verifies that Net Profit in P&L matches Current Year Earnings in Balance Sheet.
        """
        from app.modules.reports.service import ReportService
        report_service = ReportService(self.db)

        pl = await report_service.get_profit_loss(company_id, fy_id)
        bs = await report_service.get_balance_sheet(company_id, fy_id)

        net_profit = Decimal(str(pl.net_profit))

        # Check assets vs liabilities+equity
        total_assets = Decimal(str(bs.assets.total))
        total_liab_equity = Decimal(str(bs.liabilities.total)) + Decimal(str(bs.equity.total))

        # Find Net Profit in BS (usually in Equity)
        bs_net_profit = Decimal("0.00")
        for item in bs.equity.groups:
            if "profit" in item.name.lower():
                bs_net_profit = Decimal(str(item.amount))
                break

        return {
            "p_l_net_profit": float(net_profit),
            "bs_net_profit": float(bs_net_profit),
            "total_assets": float(total_assets),
            "total_liab_equity": float(total_liab_equity),
            "reconciled": abs(net_profit - bs_net_profit) < 0.01 and abs(total_assets - total_liab_equity) < 0.01
        }

    async def audit_database_consistency(self) -> List[str]:
        """
        Stage 8: Database Consistency
        """
        issues = []

        # Check for orphan VoucherEntries
        query = text("SELECT id FROM voucher_entries WHERE voucher_id NOT IN (SELECT id FROM vouchers)")
        res = await self.db.execute(query)
        if res.fetchall(): issues.append("Orphan voucher entries found.")

        # Check for duplicate voucher numbers per company/FY/type
        query = text("""
            SELECT company_id, financial_year_id, voucher_type, voucher_number, COUNT(*)
            FROM vouchers
            GROUP BY company_id, financial_year_id, voucher_type, voucher_number
            HAVING COUNT(*) > 1
        """)
        res = await self.db.execute(query)
        if res.fetchall(): issues.append("Duplicate voucher numbers detected.")

        return issues

from sqlalchemy import text
