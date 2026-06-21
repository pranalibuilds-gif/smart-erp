import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company, get_current_financial_year
from app.modules.auth.models import User
from app.modules.companies.models import Company, FinancialYear
from .service import StockAdjustmentService, StockTransferService
from .schemas.adjustments import StockAdjustmentCreate, StockAdjustmentRead
from .schemas.transfers import StockTransferCreate, StockTransferRead

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/adjustments", response_model=StandardResponse[StockAdjustmentRead], status_code=status.HTTP_201_CREATED)
async def create_adjustment(
    data: StockAdjustmentCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = StockAdjustmentService(db)
    adj = await service.create_adjustment(company.id, fy, current_user.id, data)
    return StandardResponse(success=True, data=StockAdjustmentRead.model_validate(adj), message="Draft adjustment created")


@router.get("/adjustments", response_model=StandardResponse[List[StockAdjustmentRead]])
async def list_adjustments(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = StockAdjustmentService(db)
    adjs = await service.list_adjustments(company.id, fy.id)
    return StandardResponse(success=True, data=[StockAdjustmentRead.model_validate(a) for a in adjs])


@router.get("/adjustments/{adj_id}", response_model=StandardResponse[StockAdjustmentRead])
async def get_adjustment(
    adj_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = StockAdjustmentService(db)
    adj = await service.get_adjustment(company.id, adj_id)
    return StandardResponse(success=True, data=StockAdjustmentRead.model_validate(adj))


@router.post("/adjustments/{adj_id}/post", response_model=StandardResponse[StockAdjustmentRead])
async def post_adjustment(
    adj_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = StockAdjustmentService(db)
    adj = await service.post_adjustment(company.id, adj_id, current_user.id)
    return StandardResponse(success=True, data=StockAdjustmentRead.model_validate(adj), message="Adjustment posted")


@router.post("/adjustments/{adj_id}/cancel", response_model=StandardResponse[StockAdjustmentRead])
async def cancel_adjustment(
    adj_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = StockAdjustmentService(db)
    adj = await service.cancel_adjustment(company.id, adj_id, current_user.id)
    return StandardResponse(success=True, data=StockAdjustmentRead.model_validate(adj), message="Adjustment cancelled")


# --- Stock Transfers ---

@router.post("/transfers", response_model=StandardResponse[StockTransferRead], status_code=status.HTTP_201_CREATED)
async def create_transfer(
    data: StockTransferCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = StockTransferService(db)
    trn = await service.create_transfer(company.id, fy, current_user.id, data)
    return StandardResponse(success=True, data=StockTransferRead.model_validate(trn), message="Draft transfer created")


@router.get("/transfers", response_model=StandardResponse[List[StockTransferRead]])
async def list_transfers(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = StockTransferService(db)
    trns = await service.list_transfers(company.id, fy.id)
    return StandardResponse(success=True, data=[StockTransferRead.model_validate(t) for t in trns])


@router.get("/transfers/{trn_id}", response_model=StandardResponse[StockTransferRead])
async def get_transfer(
    trn_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = StockTransferService(db)
    trn = await service.get_transfer(company.id, trn_id)
    return StandardResponse(success=True, data=StockTransferRead.model_validate(trn))


@router.post("/transfers/{trn_id}/post", response_model=StandardResponse[StockTransferRead])
async def post_transfer(
    trn_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = StockTransferService(db)
    trn = await service.post_transfer(company.id, trn_id, current_user.id)
    return StandardResponse(success=True, data=StockTransferRead.model_validate(trn), message="Transfer posted")


@router.post("/transfers/{trn_id}/cancel", response_model=StandardResponse[StockTransferRead])
async def cancel_transfer(
    trn_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = StockTransferService(db)
    trn = await service.cancel_transfer(company.id, trn_id, current_user.id)
    return StandardResponse(success=True, data=StockTransferRead.model_validate(trn), message="Transfer cancelled")
