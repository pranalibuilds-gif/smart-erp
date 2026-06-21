import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.shared.constants.business import InvitationStatus


class CompanyInvitationBase(BaseModel):
    email: EmailStr
    role_id: uuid.UUID


class CompanyInvitationCreate(CompanyInvitationBase):
    pass


class CompanyInvitationRead(CompanyInvitationBase):
    id: uuid.UUID
    company_id: uuid.UUID
    status: InvitationStatus
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    invited_by_name: Optional[str] = None
    role_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyMemberRead(BaseModel):
    user_id: uuid.UUID
    full_name: str
    email: str
    role_name: str
    is_owner: bool
    last_active_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
