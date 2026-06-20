import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.shared.constants.business import VoucherType, VoucherStatus


class VoucherEntryBase(BaseModel):
    ledger_id: uuid.UUID
    debit_amount: float = Field(0.0, ge=0)
    credit_amount: float = Field(0.0, ge=0)
    narration: Optional[str] = None


class VoucherEntryCreate(VoucherEntryBase):
    pass


class VoucherEntryRead(VoucherEntryBase):
    id: uuid.UUID
    voucher_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class VoucherBase(BaseModel):
    voucher_type: VoucherType
    voucher_date: date = Field(default_factory=date.today)
    narration: Optional[str] = None


class VoucherCreate(VoucherBase):
    # For Phase 5A, we allow creating with entries directly
    entries: List[VoucherEntryCreate] = Field(..., min_length=2)


class VoucherUpdate(BaseModel):
    voucher_date: Optional[date] = None
    narration: Optional[str] = None
    status: Optional[VoucherStatus] = None
    # Entries update might be complex, Phase 5B will handle posted immutability


class VoucherRead(VoucherBase):
    id: uuid.UUID
    company_id: uuid.UUID
    financial_year_id: uuid.UUID
    voucher_number: str
    status: VoucherStatus
    created_at: datetime
    updated_at: datetime

    entries: List[VoucherEntryRead] = []

    model_config = ConfigDict(from_attributes=True)
