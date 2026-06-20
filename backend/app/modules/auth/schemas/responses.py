import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .auth import UserRead


class AuthResponse(BaseModel):
    user: UserRead
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)
