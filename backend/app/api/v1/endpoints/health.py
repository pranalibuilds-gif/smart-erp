from fastapi import APIRouter
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()

@router.get("/health", response_model=SuccessResponse[dict[str, str]])
async def health_check():
    return SuccessResponse(data={"status": "healthy"})
