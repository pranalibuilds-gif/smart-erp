import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.shared.constants.business import AccountNature


class AccountGroupBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    nature: Optional[AccountNature] = None
    is_primary: bool = False


class AccountGroupCreate(AccountGroupBase):
    pass


class AccountGroupUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    nature: Optional[AccountNature] = None
    is_primary: Optional[bool] = None


class AccountGroupRead(AccountGroupBase):
    id: uuid.UUID
    company_id: uuid.UUID
    is_system: bool
    created_at: datetime
    updated_at: datetime

    # For recursive tree view
    subgroups: List["AccountGroupRead"] = []

    model_config = ConfigDict(from_attributes=True)
