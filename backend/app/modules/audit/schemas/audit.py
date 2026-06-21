import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    company_id: Optional[uuid.UUID] = None
    entity_type: str
    entity_id: Optional[uuid.UUID] = None
    action: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    # Optionally include user name
    user_full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
