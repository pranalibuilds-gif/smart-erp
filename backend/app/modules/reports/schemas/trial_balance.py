import uuid
from typing import List, Optional
from pydantic import BaseModel


class TrialBalanceItem(BaseModel):
    ledger_id: uuid.UUID
    ledger_name: str
    opening_balance: float
    debit_total: float
    credit_total: float
    closing_balance: float


class TrialBalanceResponse(BaseModel):
    items: List[TrialBalanceItem]
    total_debit: float
    total_credit: float
    is_balanced: bool
