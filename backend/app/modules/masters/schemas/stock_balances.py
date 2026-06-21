import uuid
from pydantic import BaseModel, ConfigDict


class StockBalanceRead(BaseModel):
    warehouse_id: uuid.UUID
    stock_item_id: uuid.UUID
    quantity: float
    average_cost: float

    model_config = ConfigDict(from_attributes=True)
