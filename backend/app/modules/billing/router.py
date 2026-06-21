import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company, get_current_financial_year
from app.modules.auth.models import User
from app.modules.companies.models import Company, FinancialYear
from .service import InvoiceService
from .schemas.invoices import InvoiceCreate, InvoiceUpdate, InvoiceRead

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/invoices", response_model=StandardResponse[InvoiceRead], status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = InvoiceService(db)
    invoice = await service.create_invoice(company.id, fy, current_user.id, data)
    return StandardResponse(success=True, data=InvoiceRead.model_validate(invoice), message="Invoice created as DRAFT")


@router.get("/invoices", response_model=StandardResponse[List[InvoiceRead]])
async def list_invoices(
    company: Company = Depends(get_current_company),
    fy: FinancialYear = Depends(get_current_financial_year),
    db: AsyncSession = Depends(get_db)
):
    service = InvoiceService(db)
    invoices = await service.list_invoices(company.id, fy.id)
    return StandardResponse(success=True, data=[InvoiceRead.model_validate(i) for i in invoices])


@router.get("/invoices/{invoice_id}", response_model=StandardResponse[InvoiceRead])
async def get_invoice(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = InvoiceService(db)
    invoice = await service.get_invoice(company.id, invoice_id)
    return StandardResponse(success=True, data=InvoiceRead.model_validate(invoice))


@router.post("/invoices/{invoice_id}/post", response_model=StandardResponse[InvoiceRead])
async def post_invoice(
    invoice_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = InvoiceService(db)
    invoice = await service.post_invoice(company.id, invoice_id, current_user.id)
    return StandardResponse(success=True, data=InvoiceRead.model_validate(invoice), message="Invoice posted and Voucher generated")


@router.post("/invoices/{invoice_id}/cancel", response_model=StandardResponse[InvoiceRead])
async def cancel_invoice(
    invoice_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = InvoiceService(db)
    invoice = await service.cancel_invoice(company.id, invoice_id, current_user.id)
    return StandardResponse(success=True, data=InvoiceRead.model_validate(invoice), message="Invoice cancelled")


@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = InvoiceService(db)
    pdf_out = await service.generate_invoice_pdf(company.id, invoice_id)

    return Response(
        content=pdf_out.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
        }
    )
