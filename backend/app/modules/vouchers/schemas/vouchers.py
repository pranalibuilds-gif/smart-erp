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
    ledger_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InventoryEntryCreate(BaseModel):
    warehouse_id: uuid.UUID
    stock_item_id: uuid.UUID
    quantity: float = Field(..., gt=0)
    rate: float = Field(..., ge=0)
    direction: Optional[int] = None # 1 for In, -1 for Out. If None, derived from VoucherType.
    narration: Optional[str] = None


class InventoryEntryRead(BaseModel):
    id: uuid.UUID
    voucher_id: uuid.UUID
    warehouse_id: uuid.UUID
    stock_item_id: uuid.UUID
    quantity: float
    rate: float
    amount: float
    direction: int

    model_config = ConfigDict(from_attributes=True)


class VoucherBase(BaseModel):
    voucher_type: VoucherType
    voucher_date: date = Field(default_factory=date.today)
    narration: Optional[str] = None


class VoucherCreate(VoucherBase):
    # For Phase 5A, we allow creating with entries directly
    entries: List[VoucherEntryCreate] = Field(..., min_length=2)
    inventory_entries: List[InventoryEntryCreate] = []


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
    inventory_entries: List[InventoryEntryRead] = []

    model_config = ConfigDict(from_attributes=True)
