import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.shared.constants.business import InvoiceStatus


class StockTransferItemBase(BaseModel):
    stock_item_id: uuid.UUID
    quantity: float = Field(..., gt=0)


class StockTransferItemCreate(StockTransferItemBase):
    pass


class StockTransferItemRead(StockTransferItemBase):
    id: uuid.UUID
    rate_snapshot: float

    model_config = ConfigDict(from_attributes=True)


class StockTransferBase(BaseModel):
    from_warehouse_id: uuid.UUID
    to_warehouse_id: uuid.UUID
    transfer_date: date = Field(default_factory=date.today)
    notes: Optional[str] = None


class StockTransferCreate(StockTransferBase):
    items: List[StockTransferItemCreate] = Field(..., min_length=1)


class StockTransferRead(StockTransferBase):
    id: uuid.UUID
    company_id: uuid.UUID
    financial_year_id: uuid.UUID
    transfer_no: str
    status: InvoiceStatus
    voucher_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    items: List[StockTransferItemRead] = []

    model_config = ConfigDict(from_attributes=True)
