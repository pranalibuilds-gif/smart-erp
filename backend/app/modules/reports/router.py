import uuid
from fastapi import APIRouter, Depends, Response
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
from .schemas.financial_statements import ProfitLossResponse, BalanceSheetResponse

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


@router.get("/profit-loss", response_model=StandardResponse[ProfitLossResponse])
async def profit_loss(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = ReportService(db)
    result = await service.get_profit_loss(company.id, fy.id)
    return StandardResponse(success=True, data=result)


@router.get("/balance-sheet", response_model=StandardResponse[BalanceSheetResponse])
async def balance_sheet(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = ReportService(db)
    result = await service.get_balance_sheet(company.id, fy.id)
    return StandardResponse(success=True, data=result)


@router.get("/trial-balance/excel")
async def export_trial_balance(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = ReportService(db)
    excel_out = await service.export_trial_balance_excel(company.id, fy.id)

    return Response(
        content=excel_out.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=trial_balance_{fy.name}.xlsx"
        }
    )
