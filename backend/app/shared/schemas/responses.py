from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str | None = None


class BaseResponse(StandardResponse[T]):
    pass

class SuccessResponse(BaseResponse[T]):
    success: bool = True

class ErrorResponse(BaseResponse[Any]):
    success: bool = False
