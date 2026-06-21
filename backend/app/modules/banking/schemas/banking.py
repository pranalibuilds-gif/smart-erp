import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BankAccountBase(BaseModel):
    ledger_id: uuid.UUID
    account_name: str
    account_number: str
    bank_name: str
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    is_active: bool = True


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountRead(BankAccountBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentAllocationBase(BaseModel):
    invoice_id: uuid.UUID
    allocated_amount: float = Field(..., gt=0)


class PaymentAllocationCreate(PaymentAllocationBase):
    pass


class PaymentAllocationRead(PaymentAllocationBase):
    id: uuid.UUID
    voucher_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class PaymentVoucherCreate(BaseModel):
    """Specific schema for Payment/Receipt vouchers with invoice allocations."""
    voucher_date: date = Field(default_factory=date.today)
    party_ledger_id: uuid.UUID
    bank_cash_ledger_id: uuid.UUID
    amount: float = Field(..., gt=0)
    narration: Optional[str] = None
    reference_no: Optional[str] = None
    allocations: List[PaymentAllocationCreate] = []
