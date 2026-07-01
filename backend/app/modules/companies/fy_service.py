import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from .models import FinancialYear, FinancialYearOpeningBalance, FinancialYearStockOpening
from app.modules.masters.models import Ledger, AccountGroup, StockItem, StockBalance, Warehouse
from app.modules.vouchers.models import Voucher, VoucherSequence, InventoryTransaction
from app.modules.billing.models import Invoice
from app.modules.inventory.models import StockAdjustment, StockTransfer
from app.modules.audit.service import AuditService
from app.shared.constants.business import BalanceType, VoucherStatus, InvoiceStatus, VoucherType, AccountNature


class FinancialYearService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)

    async def get_financial_years(self, company_id: uuid.UUID) -> Sequence[FinancialYear]:
        stmt = select(FinancialYear).where(FinancialYear.company_id == company_id).order_by(FinancialYear.start_date.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def validate_for_closing(self, fy: FinancialYear):
        # Check for draft vouchers
        stmt = select(func.count(Voucher.id)).where(and_(Voucher.financial_year_id == fy.id, Voucher.status == VoucherStatus.DRAFT))
        res = await self.db.execute(stmt)
        if res.scalar() > 0:
            raise HTTPException(status_code=400, detail="Cannot close year with draft vouchers")

        # Check for draft invoices
        stmt = select(func.count(Invoice.id)).where(and_(Invoice.financial_year_id == fy.id, Invoice.status == InvoiceStatus.DRAFT))
        res = await self.db.execute(stmt)
        if res.scalar() > 0:
            raise HTTPException(status_code=400, detail="Cannot close year with draft invoices")

        # Check for draft adjustments
        stmt = select(func.count(StockAdjustment.id)).where(and_(StockAdjustment.financial_year_id == fy.id, StockAdjustment.status == InvoiceStatus.DRAFT))
        res = await self.db.execute(stmt)
        if res.scalar() > 0:
            raise HTTPException(status_code=400, detail="Cannot close year with draft stock adjustments")

        # Check for draft transfers
        stmt = select(func.count(StockTransfer.id)).where(and_(StockTransfer.financial_year_id == fy.id, StockTransfer.status == InvoiceStatus.DRAFT))
        res = await self.db.execute(stmt)
        if res.scalar() > 0:
            raise HTTPException(status_code=400, detail="Cannot close year with draft stock transfers")

    async def close_and_rollover(self, company_id: uuid.UUID, fy_id: uuid.UUID, user_id: uuid.UUID) -> FinancialYear:
        # Hardening: Lock FY row before validation to ensure atomicity
        stmt = select(FinancialYear).where(and_(FinancialYear.id == fy_id, FinancialYear.company_id == company_id)).with_for_update()
        res = await self.db.execute(stmt)
        fy = res.scalar_one_or_none()
        if not fy:
            raise HTTPException(status_code=404, detail="Financial Year not found")

        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is already closed")

        await self.validate_for_closing(fy)

        # 1. Create Next Financial Year
        next_start = fy.end_date + timedelta(days=1)
        next_end = date(next_start.year + 1, 3, 31) if next_start.month == 4 else next_start + timedelta(days=364)
        next_name = f"{next_start.year}-{next_start.year + 1}"

        next_fy = FinancialYear(
            company_id=company_id,
            name=next_name,
            start_date=next_start,
            end_date=next_end,
            previous_fy_id=fy.id,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(next_fy)
        await self.db.flush()

        # 2. Accounting Rollover
        # Get all ledgers with their nature
        stmt = select(Ledger).where(Ledger.company_id == company_id).options(selectinload(Ledger.group))
        res = await self.db.execute(stmt)
        ledgers = res.scalars().all()

        # We need to find "Retained Earnings" or "Capital" ledger to transfer profit/loss
        # For simplicity, we assume there is a "Capital" group or we just create a "Profit & Loss" ledger if not exists.
        # Actually, let's look for a ledger named "Retained Earnings" or "Capital Account"
        stmt = select(Ledger).where(and_(Ledger.company_id == company_id, Ledger.name == "Capital"))
        res = await self.db.execute(stmt)
        capital_ledger = res.scalar_one_or_none()

        if not capital_ledger:
            # Fallback to any ledger in Liability group if "Capital" not found, or error?
            # Let's just use the first ledger in Liabilities for now or create one.
            # In a real app we'd ask the user or have a system setting.
            raise HTTPException(status_code=400, detail="Required 'Capital' ledger not found for profit/loss transfer")

        net_profit = Decimal("0.00")

        for ledger in ledgers:
            nature = ledger.group.nature
            balance = Decimal(str(ledger.current_balance))

            if nature in [AccountNature.INCOME, AccountNature.EXPENSE]:
                net_profit -= balance

                # Opening for next year is 0
                op_bal = FinancialYearOpeningBalance(
                    financial_year_id=next_fy.id,
                    ledger_id=ledger.id,
                    opening_balance=0,
                    balance_type=BalanceType.DEBIT
                )
                self.db.add(op_bal)

                # RESET current_balance for new year
                ledger.current_balance = Decimal("0.00")
                ledger.updated_by = user_id
            else:
                # Asset/Liability: Carry forward
                abs_bal = abs(balance)
                bal_type = BalanceType.DEBIT if balance >= 0 else BalanceType.CREDIT

                op_bal = FinancialYearOpeningBalance(
                    financial_year_id=next_fy.id,
                    ledger_id=ledger.id,
                    opening_balance=float(abs_bal),
                    balance_type=bal_type
                )
                self.db.add(op_bal)

                if ledger.id == capital_ledger.id:
                    capital_op_bal = op_bal

        # 2.1 Transfer Net Profit to Capital
        current_cap_val = Decimal(str(capital_op_bal.opening_balance))
        if capital_op_bal.balance_type == BalanceType.CREDIT:
             current_cap_val = -current_cap_val

        new_cap_val = current_cap_val - net_profit
        capital_op_bal.opening_balance = float(abs(new_cap_val))
        capital_op_bal.balance_type = BalanceType.DEBIT if new_cap_val >= 0 else BalanceType.CREDIT

        # Update Capital global current_balance
        capital_ledger.current_balance = new_cap_val
        capital_ledger.updated_by = user_id
        # If profit > 0, then Expense > Income -> LOSS.
        # If profit < 0, then Income > Expense -> PROFIT.

        # Wait, my logic in the loop was:
        # net_profit -= balance (where balance is ledger.current_balance)
        # Expense has positive balance (Dr). Income has negative balance (Cr).
        # net_profit = - (sum(Exp_Dr) + sum(Inc_Cr)) = sum(Inc_Cr) - sum(Exp_Dr).
        # Example: Inc_Cr = -1000, Exp_Dr = 800.
        # net_profit = - (800 + (-1000)) = - (-200) = 200.
        # Wait, if Income > Expense, net_profit should be positive (Profit).
        # Inc_Cr = -1000, Exp_Dr = 800.
        # net_profit = (-Inc_Cr) - (Exp_Dr) = 1000 - 800 = 200.

        # Current logic:
        # Profit = 0
        # For Income: Profit -= (-1000) -> Profit = 1000
        # For Expense: Profit -= (800) -> Profit = 200.
        # Correct! Positive net_profit = Profit.

        # Now update Capital opening balance.
        # Capital usually has Credit balance (negative in our logic).
        # Current Capital opening balance = capital_op_bal.opening_balance (abs) with bal_type.

        current_cap_val = Decimal(str(capital_op_bal.opening_balance))
        if capital_op_bal.balance_type == BalanceType.CREDIT:
             current_cap_val = -current_cap_val

        # New Capital = Old Capital + Net Profit (Profit increases Credit)
        # Wait, Credit is negative. So New Capital = current_cap_val - net_profit?
        # Example: Cap = -5000 (Cr). Profit = 200. New Cap = -5200 (Cr).
        # Yes: -5000 - 200 = -5200.

        new_cap_val = current_cap_val - net_profit
        capital_op_bal.opening_balance = float(abs(new_cap_val))
        capital_op_bal.balance_type = BalanceType.DEBIT if new_cap_val >= 0 else BalanceType.CREDIT

        # 3. Inventory Rollover
        # Get all StockBalances
        stmt = select(StockBalance).join(StockItem).where(StockItem.company_id == company_id)
        res = await self.db.execute(stmt)
        stock_balances = res.scalars().all()

        for sb in stock_balances:
            stock_op = FinancialYearStockOpening(
                financial_year_id=next_fy.id,
                stock_item_id=sb.stock_item_id,
                warehouse_id=sb.warehouse_id,
                quantity=sb.quantity,
                average_cost=sb.average_cost
            )
            self.db.add(stock_op)

        # 4. Reset Voucher Sequences
        # Just don't create any, they will be created on first voucher of next year.

        # 5. Mark FY as closed
        fy.is_closed = True
        fy.updated_by = user_id

        await self.db.commit()

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="FINANCIAL_YEAR",
            entity_id=fy.id,
            action="CLOSE",
            new_values={"is_closed": True, "next_fy_id": str(next_fy.id)}
        )
        await self.db.commit()

        return fy
