import uuid
from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class LedgerEntryItem(BaseModel):
    date: date
    voucher_number: str
    voucher_type: str
    narration: Optional[str] = None
    debit: float
    credit: float
    running_balance: float


class GeneralLedgerResponse(BaseModel):
    ledger_id: uuid.UUID
    ledger_name: str
    opening_balance: float
    entries: List[LedgerEntryItem]
    closing_balance: float
