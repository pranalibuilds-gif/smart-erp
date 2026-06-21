import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.shared.constants.business import InvoiceStatus


class StockAdjustmentItemBase(BaseModel):
    stock_item_id: uuid.UUID
    physical_quantity: float = Field(..., ge=0)


class StockAdjustmentItemCreate(StockAdjustmentItemBase):
    pass


class StockAdjustmentItemRead(StockAdjustmentItemBase):
    id: uuid.UUID
    system_quantity: float
    difference_quantity: float
    rate_snapshot: float

    model_config = ConfigDict(from_attributes=True)


class StockAdjustmentBase(BaseModel):
    warehouse_id: uuid.UUID
    adjustment_date: date = Field(default_factory=date.today)
    reason: Optional[str] = None
    notes: Optional[str] = None


class StockAdjustmentCreate(StockAdjustmentBase):
    items: List[StockAdjustmentItemCreate] = Field(..., min_length=1)


class StockAdjustmentRead(StockAdjustmentBase):
    id: uuid.UUID
    company_id: uuid.UUID
    financial_year_id: uuid.UUID
    adjustment_no: str
    status: InvoiceStatus
    voucher_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    items: List[StockAdjustmentItemRead] = []

    model_config = ConfigDict(from_attributes=True)
