import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_company
from app.modules.companies.models import Company
from .service import SearchService
from .schemas.search import SearchResult

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=StandardResponse[List[SearchResult]])
async def global_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, le=50),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = SearchService(db)
    results = await service.search(company.id, q, limit)
    return StandardResponse(success=True, data=[SearchResult.model_validate(r) for r in results])
