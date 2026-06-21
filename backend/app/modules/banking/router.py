import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company, get_current_financial_year
from app.modules.auth.models import User
from app.modules.companies.models import Company, FinancialYear
from app.modules.vouchers.schemas.vouchers import VoucherRead
from .service import BankingService
from .schemas.banking import BankAccountCreate, BankAccountRead, PaymentVoucherCreate
from .schemas.statements import BankStatementCreate, BankStatementRead, BankStatementLineRead

router = APIRouter(prefix="/banking", tags=["Banking"])


@router.post("/bank-accounts", response_model=StandardResponse[BankAccountRead], status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    data: BankAccountCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = BankingService(db)
    account = await service.create_bank_account(company.id, current_user.id, data)
    return StandardResponse(success=True, data=BankAccountRead.model_validate(account), message="Bank account linked")


@router.get("/bank-accounts", response_model=StandardResponse[List[BankAccountRead]])
async def list_bank_accounts(
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = BankingService(db)
    accounts = await service.get_bank_accounts(company.id)
    return StandardResponse(success=True, data=[BankAccountRead.model_validate(a) for a in accounts])


@router.post("/payments", response_model=StandardResponse[VoucherRead], status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentVoucherCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = BankingService(db)
    voucher = await service.create_payment_or_receipt(company.id, fy, current_user.id, data, is_receipt=False)
    return StandardResponse(success=True, data=VoucherRead.model_validate(voucher), message="Payment recorded and posted")


@router.post("/receipts", response_model=StandardResponse[VoucherRead], status_code=status.HTTP_201_CREATED)
async def create_receipt(
    data: PaymentVoucherCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = BankingService(db)
    voucher = await service.create_payment_or_receipt(company.id, fy, current_user.id, data, is_receipt=True)
    return StandardResponse(success=True, data=VoucherRead.model_validate(voucher), message="Receipt recorded and posted")


@router.get("/invoices/{invoice_id}/outstanding", response_model=StandardResponse[float])
async def get_invoice_outstanding(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    service = BankingService(db)
    outstanding = await service.get_invoice_outstanding(invoice_id)
    return StandardResponse(success=True, data=float(outstanding))


@router.post("/statements", response_model=StandardResponse[BankStatementRead], status_code=status.HTTP_201_CREATED)
async def import_statement(
    data: BankStatementCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = BankingService(db)
    statement = await service.import_bank_statement(company.id, current_user.id, data)
    return StandardResponse(success=True, data=BankStatementRead.model_validate(statement), message="Bank statement imported")


@router.post("/statement-lines/{line_id}/reconcile", response_model=StandardResponse[BankStatementLineRead])
async def reconcile_statement_line(
    line_id: uuid.UUID,
    voucher_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    service = BankingService(db)
    line = await service.reconcile_line(line_id, voucher_id)
    return StandardResponse(success=True, data=BankStatementLineRead.model_validate(line), message="Line reconciled")
