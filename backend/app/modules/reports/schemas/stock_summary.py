import uuid
from typing import List
from pydantic import BaseModel


class StockSummaryItem(BaseModel):
    item_id: uuid.UUID
    item_name: str
    opening_qty: float = 0
    inward_qty: float
    outward_qty: float
    closing_qty: float
    average_cost: float
    stock_value: float


class StockSummaryResponse(BaseModel):
    items: List[StockSummaryItem]
    total_value: float
