import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UnitBase(BaseModel):
    name: str
    description: Optional[str] = None


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class UnitRead(UnitBase):
    id: uuid.UUID
    company_id: uuid.UUID
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
