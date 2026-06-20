import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.shared.constants.business import BalanceType


class LedgerBase(BaseModel):
    name: str
    group_id: uuid.UUID
    code: Optional[str] = None
    opening_balance: float = Field(default=0.0, ge=0)
    opening_balance_type: BalanceType = BalanceType.DEBIT
    is_active: bool = True


class LedgerCreate(LedgerBase):
    pass


class LedgerUpdate(BaseModel):
    name: Optional[str] = None
    group_id: Optional[uuid.UUID] = None
    code: Optional[str] = None
    opening_balance: Optional[float] = Field(None, ge=0)
    opening_balance_type: Optional[BalanceType] = None
    is_active: Optional[bool] = None


class LedgerRead(LedgerBase):
    id: uuid.UUID
    company_id: uuid.UUID
    current_balance: float
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
