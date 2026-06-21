import uuid
from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class WarehouseStockItem(BaseModel):
    item_id: uuid.UUID
    item_name: str
    quantity: float
    average_cost: float
    value: float


class WarehouseStockResponse(BaseModel):
    warehouse_name: str
    items: List[WarehouseStockItem]
    total_value: float


class TransferReportItem(BaseModel):
    id: uuid.UUID
    transfer_no: str
    date: date
    from_warehouse: str
    to_warehouse: str
    item_count: int
    status: str


class AdjustmentReportItem(BaseModel):
    id: uuid.UUID
    adjustment_no: str
    date: date
    warehouse_name: str
    reason: Optional[str]
    status: str
