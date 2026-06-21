import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SearchResult(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    title: str
    subtitle: Optional[str] = None
    url: str

    model_config = ConfigDict(from_attributes=True)
