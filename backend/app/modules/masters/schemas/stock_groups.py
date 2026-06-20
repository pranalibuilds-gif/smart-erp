import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class StockGroupBase(BaseModel):
    name: str
    parent_id: Optional[uuid.UUID] = None


class StockGroupCreate(StockGroupBase):
    pass


class StockGroupUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class StockGroupRead(StockGroupBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    subgroups: List["StockGroupRead"] = []

    model_config = ConfigDict(from_attributes=True)
