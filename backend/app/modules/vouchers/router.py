import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company, get_current_financial_year, PermissionRequired
from app.modules.auth.models import User
from app.modules.companies.models import Company, FinancialYear
from .service import VoucherService
from .schemas.vouchers import VoucherCreate, VoucherUpdate, VoucherRead

router = APIRouter(prefix="/vouchers", tags=["Vouchers"])


@router.post(
    "",
    response_model=StandardResponse[VoucherRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("voucher:create"))]
)
async def create_voucher(
    data: VoucherCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = VoucherService(db)
    voucher = await service.create_voucher(company.id, fy, current_user.id, data)
    return StandardResponse(success=True, data=VoucherRead.model_validate(voucher), message="Voucher created")


@router.get(
    "",
    response_model=StandardResponse[List[VoucherRead]],
    dependencies=[Depends(PermissionRequired("voucher:view"))]
)
async def list_vouchers(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = VoucherService(db)
    vouchers = await service.list_vouchers(company.id, fy.id)

    data = []
    for v in vouchers:
        v_read = VoucherRead.model_validate(v)
        # Map ledger names
        for i, entry in enumerate(v.entries):
            v_read.entries[i].ledger_name = entry.ledger.name if entry.ledger else None
        data.append(v_read)

    return StandardResponse(success=True, data=data)


@router.get(
    "/{voucher_id}",
    response_model=StandardResponse[VoucherRead],
    dependencies=[Depends(PermissionRequired("voucher:view"))]
)
async def get_voucher(
    voucher_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = VoucherService(db)
    voucher = await service.get_voucher(company.id, voucher_id)
    return StandardResponse(success=True, data=VoucherRead.model_validate(voucher))


@router.post(
    "/{voucher_id}/post",
    response_model=StandardResponse[VoucherRead],
    dependencies=[Depends(PermissionRequired("voucher:post"))]
)
async def post_voucher(
    voucher_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = VoucherService(db)
    voucher = await service.post_voucher(company.id, voucher_id, current_user.id)
    return StandardResponse(success=True, data=VoucherRead.model_validate(voucher), message="Voucher posted")


@router.post(
    "/{voucher_id}/cancel",
    response_model=StandardResponse[VoucherRead],
    dependencies=[Depends(PermissionRequired("voucher:cancel"))]
)
async def cancel_voucher(
    voucher_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = VoucherService(db)
    voucher = await service.cancel_voucher(company.id, voucher_id, current_user.id)
    return StandardResponse(success=True, data=VoucherRead.model_validate(voucher), message="Voucher cancelled")
