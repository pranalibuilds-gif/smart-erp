import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.shared.constants.business import DocumentType, InvoiceStatus


class InvoiceItemBase(BaseModel):
    stock_item_id: Optional[uuid.UUID] = None
    item_name: str
    item_code: Optional[str] = None
    unit_name: Optional[str] = None
    hsn_code: Optional[str] = None
    quantity: float = Field(..., gt=0)
    rate: float = Field(..., ge=0)
    tax_rate: float = Field(0.0, ge=0)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemRead(InvoiceItemBase):
    id: uuid.UUID
    invoice_id: uuid.UUID
    taxable_amount: float
    tax_amount: float
    total_amount: float

    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    party_id: uuid.UUID
    document_type: DocumentType
    invoice_date: date = Field(default_factory=date.today)
    narration: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = Field(..., min_length=1)


class InvoiceUpdate(BaseModel):
    invoice_date: Optional[date] = None
    narration: Optional[str] = None
    # Posted invoices are immutable


class InvoiceRead(InvoiceBase):
    id: uuid.UUID
    company_id: uuid.UUID
    financial_year_id: uuid.UUID
    voucher_id: Optional[uuid.UUID] = None
    invoice_number: str
    status: InvoiceStatus
    taxable_amount: float
    tax_amount: float
    total_amount: float
    created_at: datetime
    updated_at: datetime

    items: List[InvoiceItemRead] = []

    model_config = ConfigDict(from_attributes=True)
