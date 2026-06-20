import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PartyBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    gstin: Optional[str] = Field(None, max_length=15)
    pan: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = None
    credit_limit: float = Field(0.0, ge=0)
    is_customer: bool = True
    is_supplier: bool = False
    is_active: bool = True


class PartyCreate(PartyBase):
    pass


class PartyUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Optional[float] = None
    is_customer: Optional[bool] = None
    is_supplier: Optional[bool] = None
    is_active: Optional[bool] = None


class PartyRead(PartyBase):
    id: uuid.UUID
    company_id: uuid.UUID
    ledger_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Placeholder for dynamic field
    outstanding_balance: float = 0.0

    model_config = ConfigDict(from_attributes=True)
