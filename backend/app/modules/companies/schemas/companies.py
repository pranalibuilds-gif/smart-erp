import uuid
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class CompanyBase(BaseModel):
    name: str
    legal_name: str
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    state: str | None = None
    country: str = "India"
    gst_number: str | None = None
    logo_url: str | None = None


class CompanyCreate(CompanyBase):
    # Required for initial FY creation
    financial_year_start: date


class CompanyUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    state: str | None = None
    country: str | None = None
    gst_number: str | None = None
    logo_url: str | None = None
    is_active: bool | None = None


class CompanyRead(CompanyBase):
    id: uuid.UUID
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
