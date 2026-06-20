import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.shared.constants.business import ItemType


class StockItemBase(BaseModel):
    name: str
    stock_group_id: Optional[uuid.UUID] = None
    unit_id: uuid.UUID
    sku: Optional[str] = None
    item_type: ItemType = ItemType.PRODUCT
    is_active: bool = True


class StockItemCreate(StockItemBase):
    pass


class StockItemUpdate(BaseModel):
    name: Optional[str] = None
    stock_group_id: Optional[uuid.UUID] = None
    unit_id: Optional[uuid.UUID] = None
    sku: Optional[str] = None
    item_type: Optional[ItemType] = None
    is_active: Optional[bool] = None


class StockItemRead(StockItemBase):
    id: uuid.UUID
    company_id: uuid.UUID
    current_quantity: float
    average_cost: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
