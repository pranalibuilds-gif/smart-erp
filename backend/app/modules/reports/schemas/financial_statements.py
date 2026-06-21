from typing import List, Dict
from pydantic import BaseModel


class FinancialStatementItem(BaseModel):
    name: str
    amount: float


class ProfitLossResponse(BaseModel):
    income: List[FinancialStatementItem]
    expenses: List[FinancialStatementItem]
    total_income: float
    total_expenses: float
    net_profit: float


class BalanceSheetSection(BaseModel):
    groups: List[FinancialStatementItem]
    total: float


class BalanceSheetResponse(BaseModel):
    assets: BalanceSheetSection
    liabilities: BalanceSheetSection
    equity: BalanceSheetSection
    is_balanced: bool
