import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, field_validator


class FinancialYearBase(BaseModel):
    name: str
    start_date: date
    end_date: date


class FinancialYearCreate(FinancialYearBase):
    pass


class FinancialYearRead(FinancialYearBase):
    id: uuid.UUID
    company_id: uuid.UUID
    is_closed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date, info):
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v
