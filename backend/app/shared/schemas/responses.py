from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str | None = None

class SuccessResponse(BaseResponse[T]):
    success: bool = True

class ErrorResponse(BaseResponse[None]):
    success: bool = False
