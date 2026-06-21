import uuid
from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from .queries.trial_balance import get_trial_balance_data
from .queries.general_ledger import get_ledger_entries
from .queries.stock_summary import get_stock_summary_data
from .schemas.trial_balance import TrialBalanceItem, TrialBalanceResponse
from .schemas.general_ledger import LedgerEntryItem, GeneralLedgerResponse
from .schemas.stock_summary import StockSummaryItem, StockSummaryResponse
from .schemas.dashboard import DashboardMetrics
from app.modules.masters.models import Ledger


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_trial_balance(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> TrialBalanceResponse:
        data = await get_trial_balance_data(self.db, company_id, fy_id)

        items = []
        grand_total_debit = Decimal("0.00")
        grand_total_credit = Decimal("0.00")

        for row in data:
            opening = Decimal(str(row.opening_balance))
            # Adjust opening based on type
            if row.opening_balance_type == "CREDIT":
                opening = -opening

            debit = Decimal(str(row.debit_total))
            credit = Decimal(str(row.credit_total))
            closing = opening + debit - credit

            items.append(TrialBalanceItem(
                ledger_id=row.ledger_id,
                ledger_name=row.ledger_name,
                opening_balance=float(opening),
                debit_total=float(debit),
                credit_total=float(credit),
                closing_balance=float(closing)
            ))
            grand_total_debit += debit
            grand_total_credit += credit

        return TrialBalanceResponse(
            items=items,
            total_debit=float(grand_total_debit),
            total_credit=float(grand_total_credit),
            is_balanced=abs(grand_total_debit - grand_total_credit) < 0.01
        )

    async def get_general_ledger(self, company_id: uuid.UUID, fy_id: uuid.UUID, ledger_id: uuid.UUID) -> GeneralLedgerResponse:
        ledger = await self.db.get(Ledger, ledger_id)
        if not ledger or ledger.company_id != company_id:
            raise HTTPException(status_code=404, detail="Ledger not found")

        opening = Decimal(str(ledger.opening_balance))
        if ledger.opening_balance_type == "CREDIT":
            opening = -opening

        rows = await get_ledger_entries(self.db, company_id, fy_id, ledger_id)

        entries = []
        current_bal = opening
        for row in rows:
            dr = Decimal(str(row.debit))
            cr = Decimal(str(row.credit))
            current_bal += (dr - cr)
            entries.append(LedgerEntryItem(
                date=row.date,
                voucher_number=row.voucher_number,
                voucher_type=row.voucher_type,
                narration=row.narration,
                debit=float(dr),
                credit=float(cr),
                running_balance=float(current_bal)
            ))

        return GeneralLedgerResponse(
            ledger_id=ledger.id,
            ledger_name=ledger.name,
            opening_balance=float(opening),
            entries=entries,
            closing_balance=float(current_bal)
        )

    async def get_stock_summary(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> StockSummaryResponse:
        data = await get_stock_summary_data(self.db, company_id, fy_id)

        items = []
        total_value = Decimal("0.00")

        for row in data:
            opening_qty = 0.0 # TODO: handle opening stock
            inward = float(row.inward_qty)
            outward = float(row.outward_qty)
            closing = opening_qty + inward - outward

            avg_cost = Decimal(str(row.average_cost))
            value = Decimal(str(closing)) * avg_cost

            items.append(StockSummaryItem(
                item_id=row.item_id,
                item_name=row.item_name,
                opening_qty=opening_qty,
                inward_qty=inward,
                outward_qty=outward,
                closing_qty=closing,
                average_cost=float(avg_cost),
                stock_value=float(value)
            ))
            total_value += value

        return StockSummaryResponse(
            items=items,
            total_value=float(total_value)
        )

    async def get_dashboard_metrics(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> DashboardMetrics:
        # Implementation of dashboard metrics using existing report logic
        # 1. Total Sales from Trial Balance (Income nature)
        # 2. Total Purchases from Trial Balance (Expense nature)
        # 3. Total Receivables (Sundry Debtors)
        # 4. Total Payables (Sundry Creditors)
        # 5. Inventory Value from Stock Summary

        tb = await self.get_trial_balance(company_id, fy_id)
        stock = await self.get_stock_summary(company_id, fy_id)

        # This is simplified. In a real ERP, we filter by account group name or nature.
        # Since we seeded groups:
        sales = sum(item.credit_total for item in tb.items if "Sales" in item.ledger_name)
        purchases = sum(item.debit_total for item in tb.items if "Purchase" in item.ledger_name)

        # Receivables usually have Debit balance
        receivables = sum(item.closing_balance for item in tb.items if item.closing_balance > 0)
        # This is very rough, should ideally check if parent group is Sundry Debtors

        return DashboardMetrics(
            total_sales=float(sales),
            total_purchases=float(purchases),
            total_receivables=float(receivables),
            total_payables=0.0, # Placeholder
            inventory_value=stock.total_value
        )
