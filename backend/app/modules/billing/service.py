import uuid
import io
import os
from decimal import Decimal
from typing import List, Sequence
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

from .models import Invoice, InvoiceItem
from .schemas.invoices import InvoiceCreate, InvoiceUpdate
from app.modules.companies.models import FinancialYear
from app.modules.parties.models import Party
from app.modules.vouchers.service import VoucherService
from app.modules.vouchers.schemas.vouchers import VoucherCreate, VoucherEntryCreate, InventoryEntryCreate
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.business import DocumentType, InvoiceStatus, VoucherType


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.invoice_repo = SQLAlchemyRepository(db, Invoice)

    async def _generate_invoice_number(self, company_id: uuid.UUID, fy: FinancialYear, doc_type: DocumentType) -> str:
        # For simplicity, using a basic counter. In production, use a numbering scheme similar to vouchers.
        from sqlalchemy import func
        stmt = select(func.count(Invoice.id)).where(
            and_(
                Invoice.company_id == company_id,
                Invoice.financial_year_id == fy.id,
                Invoice.document_type == doc_type
            )
        )
        res = await self.db.execute(stmt)
        count = res.scalar() or 0

        prefix = "INV" if doc_type == DocumentType.SALES else "PUR"
        return f"{prefix}/{fy.name[2:4]}-{fy.name[7:9]}/{(count + 1):06d}"

    async def create_invoice(self, company_id: uuid.UUID, fy: FinancialYear, user_id: uuid.UUID, data: InvoiceCreate) -> Invoice:
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        # Validate Party
        stmt = select(Party).where(and_(Party.id == data.party_id, Party.company_id == company_id))
        res = await self.db.execute(stmt)
        party = res.scalar_one_or_none()
        if not party:
            raise HTTPException(status_code=400, detail="Invalid party")

        # Generate number
        inv_number = await self._generate_invoice_number(company_id, fy, data.document_type)

        invoice = Invoice(
            company_id=company_id,
            financial_year_id=fy.id,
            party_id=data.party_id,
            document_type=data.document_type,
            invoice_number=inv_number,
            invoice_date=data.invoice_date,
            narration=data.narration,
            status=InvoiceStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(invoice)
        await self.db.flush()

        total_taxable = Decimal("0.00")
        total_tax = Decimal("0.00")

        for item_data in data.items:
            taxable = Decimal(str(item_data.quantity)) * Decimal(str(item_data.rate))
            tax = taxable * (Decimal(str(item_data.tax_rate)) / Decimal("100"))
            total = taxable + tax

            item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data.model_dump(),
                taxable_amount=taxable,
                tax_amount=tax,
                total_amount=total
            )
            self.db.add(item)
            total_taxable += taxable
            total_tax += tax

        invoice.taxable_amount = total_taxable
        invoice.tax_amount = total_tax
        invoice.total_amount = total_taxable + total_tax

        await self.db.commit()
        await self.db.refresh(invoice, ["items"])
        return invoice

    async def list_invoices(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> Sequence[Invoice]:
        stmt = select(Invoice).where(
            and_(Invoice.company_id == company_id, Invoice.financial_year_id == fy_id)
        ).options(selectinload(Invoice.items)).order_by(Invoice.invoice_date.desc(), Invoice.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_invoice(self, company_id: uuid.UUID, invoice_id: uuid.UUID) -> Invoice:
        stmt = select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.company_id == company_id)
        ).options(selectinload(Invoice.items))
        result = await self.db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice

    async def post_invoice(self, company_id: uuid.UUID, invoice_id: uuid.UUID, user_id: uuid.UUID) -> Invoice:
        invoice = await self.get_invoice(company_id, invoice_id)
        if invoice.status != InvoiceStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Only draft invoices can be posted")

        # 1. Prepare Voucher Data
        v_type = VoucherType.SALES if invoice.document_type == DocumentType.SALES else VoucherType.PURCHASE

        # Determine Ledgers (In a real ERP, these are configurable)
        # Sales: Dr Party, Cr Sales Account
        # Purchase: Dr Purchase Account, Cr Party

        party = await self.db.get(Party, invoice.party_id)

        # Find Sales/Purchase Ledger
        from app.modules.masters.models import Ledger
        ledger_name = "Sales" if invoice.document_type == DocumentType.SALES else "Purchase"
        stmt = select(Ledger).where(and_(Ledger.company_id == company_id, Ledger.name == ledger_name))
        res = await self.db.execute(stmt)
        trade_ledger = res.scalar_one_or_none()
        if not trade_ledger:
            raise HTTPException(status_code=400, detail=f"Required ledger '{ledger_name}' not found")

        entries = []
        if invoice.document_type == DocumentType.SALES:
            # Dr Party
            entries.append(VoucherEntryCreate(ledger_id=party.ledger_id, debit_amount=invoice.total_amount, credit_amount=0))
            # Cr Sales
            entries.append(VoucherEntryCreate(ledger_id=trade_ledger.id, debit_amount=0, credit_amount=invoice.total_amount))
        else:
            # Dr Purchase
            entries.append(VoucherEntryCreate(ledger_id=trade_ledger.id, debit_amount=invoice.total_amount, credit_amount=0))
            # Cr Party
            entries.append(VoucherEntryCreate(ledger_id=party.ledger_id, debit_amount=0, credit_amount=invoice.total_amount))

        inventory_entries = []
        for item in invoice.items:
            if item.stock_item_id:
                inventory_entries.append(InventoryEntryCreate(
                    stock_item_id=item.stock_item_id,
                    quantity=item.quantity,
                    rate=item.rate,
                    narration=f"Ref: {invoice.invoice_number}"
                ))

        # 2. Create and Post Voucher
        v_service = VoucherService(self.db)
        fy = await self.db.get(FinancialYear, invoice.financial_year_id)

        v_data = VoucherCreate(
            voucher_type=v_type,
            voucher_date=invoice.invoice_date,
            narration=f"Generated from Invoice {invoice.invoice_number}",
            entries=entries,
            inventory_entries=inventory_entries
        )

        voucher = await v_service.create_voucher(company_id, fy, user_id, v_data)
        await v_service.post_voucher(company_id, voucher.id, user_id)

        # 3. Link Voucher and Update Status
        invoice.voucher_id = voucher.id
        invoice.status = InvoiceStatus.POSTED
        invoice.updated_by = user_id

        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

    async def cancel_invoice(self, company_id: uuid.UUID, invoice_id: uuid.UUID, user_id: uuid.UUID) -> Invoice:
        invoice = await self.get_invoice(company_id, invoice_id)
        if invoice.status == InvoiceStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Invoice already cancelled")

        if invoice.status == InvoiceStatus.POSTED and invoice.voucher_id:
            v_service = VoucherService(self.db)
            await v_service.cancel_voucher(company_id, invoice.voucher_id, user_id)

        invoice.status = InvoiceStatus.CANCELLED
        invoice.updated_by = user_id

        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

    async def generate_invoice_pdf(self, company_id: uuid.UUID, invoice_id: uuid.UUID) -> io.BytesIO:
        invoice = await self.get_invoice(company_id, invoice_id)
        from app.modules.companies.models import Company
        company = await self.db.get(Company, company_id)
        party = await self.db.get(Party, invoice.party_id)

        # Setup Jinja2
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("invoice.html")

        html_out = template.render(
            invoice=invoice,
            company=company,
            party=party
        )

        pdf_out = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.BytesIO(html_out.encode("utf-8")), dest=pdf_out)

        if pisa_status.err:
            raise HTTPException(status_code=500, detail="PDF generation failed")

        pdf_out.seek(0)
        return pdf_out
