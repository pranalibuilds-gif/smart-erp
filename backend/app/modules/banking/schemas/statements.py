import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BankStatementLineBase(BaseModel):
    txn_date: date
    description: str
    amount: float
    reference: Optional[str] = None


class BankStatementLineCreate(BankStatementLineBase):
    pass


class BankStatementLineRead(BankStatementLineBase):
    id: uuid.UUID
    is_reconciled: bool
    voucher_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class BankStatementBase(BaseModel):
    bank_ledger_id: uuid.UUID
    statement_date: date
    opening_balance: float
    closing_balance: float
    notes: Optional[str] = None


class BankStatementCreate(BankStatementBase):
    lines: List[BankStatementLineCreate] = Field(..., min_length=1)


class BankStatementRead(BankStatementBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime

    lines: List[BankStatementLineRead] = []

    model_config = ConfigDict(from_attributes=True)
