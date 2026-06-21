import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from .service import CompanyService
from .fy_service import FinancialYearService
from .schemas import CompanyCreate, CompanyRead, FinancialYearRead

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=StandardResponse[CompanyRead], status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)
    company = await service.create_company(current_user.id, data)
    return StandardResponse(
        success=True,
        data=CompanyRead.model_validate(company),
        message="Company created successfully"
    )


@router.get("", response_model=StandardResponse[List[CompanyRead]])
async def list_user_companies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)
    companies = await service.get_user_companies(current_user.id)
    return StandardResponse(
        success=True,
        data=[CompanyRead.model_validate(c) for c in companies],
        message="User companies retrieved successfully"
    )


@router.get("/{company_id}", response_model=StandardResponse[CompanyRead])
async def get_company(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)
    company = await service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if user has access (TODO: use permission guards)
    # For now simple check
    companies = await service.get_user_companies(current_user.id)
    if company.id not in [c.id for c in companies]:
         raise HTTPException(status_code=403, detail="Not enough permissions")

    return StandardResponse(
        success=True,
        data=CompanyRead.model_validate(company),
        message="Company retrieved successfully"
    )

@router.get("/{company_id}/financial-years", response_model=StandardResponse[List[FinancialYearRead]])
async def list_financial_years(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    from .models import FinancialYear

    # Check access
    service = CompanyService(db)
    companies = await service.get_user_companies(current_user.id)
    if company_id not in [c.id for c in companies]:
         raise HTTPException(status_code=403, detail="Not enough permissions")

    stmt = select(FinancialYear).where(FinancialYear.company_id == company_id)
    result = await db.execute(stmt)
    years = result.scalars().all()

    return StandardResponse(
        success=True,
        data=[FinancialYearRead.model_validate(y) for y in years],
        message="Financial years retrieved successfully"
    )


@router.post("/{company_id}/financial-years/{fy_id}/close", response_model=StandardResponse[FinancialYearRead])
async def close_financial_year(
    company_id: uuid.UUID,
    fy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = FinancialYearService(db)
    fy = await service.close_and_rollover(company_id, fy_id, current_user.id)
    return StandardResponse(
        success=True,
        data=FinancialYearRead.model_validate(fy),
        message="Financial year closed successfully and next year created"
    )
