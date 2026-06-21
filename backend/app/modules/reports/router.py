import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_company, get_current_financial_year
from app.modules.companies.models import Company, FinancialYear
from .service import ReportService
from .schemas.trial_balance import TrialBalanceResponse
from .schemas.general_ledger import GeneralLedgerResponse
from .schemas.stock_summary import StockSummaryResponse
from .schemas.dashboard import DashboardMetrics

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/trial-balance", response_model=StandardResponse[TrialBalanceResponse])
async def trial_balance(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = ReportService(db)
    result = await service.get_trial_balance(company.id, fy.id)
    return StandardResponse(success=True, data=result)


@router.get("/general-ledger/{ledger_id}", response_model=StandardResponse[GeneralLedgerResponse])
async def general_ledger(
    ledger_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = ReportService(db)
    result = await service.get_general_ledger(company.id, fy.id, ledger_id)
    return StandardResponse(success=True, data=result)


@router.get("/stock-summary", response_model=StandardResponse[StockSummaryResponse])
async def stock_summary(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = ReportService(db)
    result = await service.get_stock_summary(company.id, fy.id)
    return StandardResponse(success=True, data=result)


@router.get("/dashboard-metrics", response_model=StandardResponse[DashboardMetrics])
async def dashboard_metrics(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = ReportService(db)
    result = await service.get_dashboard_metrics(company.id, fy.id)
    return StandardResponse(success=True, data=result)
