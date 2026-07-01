import uuid
from decimal import Decimal
from typing import List, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException

from .models import BankAccount, PaymentAllocation, BankStatement, BankStatementLine
from .schemas.banking import BankAccountCreate, PaymentVoucherCreate
from .schemas.statements import BankStatementCreate
from app.modules.masters.models import Ledger
from app.modules.vouchers.models import Voucher
from app.modules.vouchers.service import VoucherService
from app.modules.vouchers.schemas.vouchers import VoucherCreate, VoucherEntryCreate
from app.modules.billing.models import Invoice
from app.modules.companies.models import FinancialYear
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.business import VoucherType, LedgerType


class BankingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.bank_repo = SQLAlchemyRepository(db, BankAccount)
        self.voucher_service = VoucherService(db)

    async def create_bank_account(self, company_id: uuid.UUID, user_id: uuid.UUID, data: BankAccountCreate) -> BankAccount:
        # Verify ledger exists and belongs to company
        ledger = await self.db.get(Ledger, data.ledger_id)
        if not ledger or ledger.company_id != company_id:
            raise HTTPException(status_code=400, detail="Invalid ledger")

        # Tag ledger as BANK if not already
        ledger.ledger_type = LedgerType.BANK

        bank_account = BankAccount(
            **data.model_dump(),
            company_id=company_id,
            created_by=user_id,
            updated_by=user_id
        )
        return await self.bank_repo.create(bank_account)

    async def get_bank_accounts(self, company_id: uuid.UUID) -> Sequence[BankAccount]:
        stmt = select(BankAccount).where(BankAccount.company_id == company_id)
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create_payment_or_receipt(
        self,
        company_id: uuid.UUID,
        fy: FinancialYear,
        user_id: uuid.UUID,
        data: PaymentVoucherCreate,
        is_receipt: bool
    ) -> Voucher:
        """
        Orchestrates creation of a Payment or Receipt voucher with invoice allocations.
        """
        v_type = VoucherType.RECEIPT if is_receipt else VoucherType.PAYMENT

        # 1. Create Voucher Entries
        entries = []
        if is_receipt:
            # Receipt: Dr Bank/Cash, Cr Party
            entries.append(VoucherEntryCreate(ledger_id=data.bank_cash_ledger_id, debit_amount=data.amount, credit_amount=0))
            entries.append(VoucherEntryCreate(ledger_id=data.party_ledger_id, debit_amount=0, credit_amount=data.amount))
        else:
            # Payment: Dr Party, Cr Bank/Cash
            entries.append(VoucherEntryCreate(ledger_id=data.party_ledger_id, debit_amount=data.amount, credit_amount=0))
            entries.append(VoucherEntryCreate(ledger_id=data.bank_cash_ledger_id, debit_amount=0, credit_amount=data.amount))

        v_data = VoucherCreate(
            voucher_type=v_type,
            voucher_date=data.voucher_date,
            narration=data.narration,
            entries=entries
        )

        # 2. Create and Post Voucher
        voucher = await self.voucher_service.create_voucher(company_id, fy, user_id, v_data)
        await self.voucher_service.post_voucher(company_id, voucher.id, user_id)

        # 3. Handle Allocations
        total_allocated = Decimal("0.00")
        for alloc_data in data.allocations:
            # Verify invoice belongs to company
            invoice = await self.db.get(Invoice, alloc_data.invoice_id)
            if not invoice or invoice.company_id != company_id:
                raise HTTPException(status_code=400, detail=f"Invalid invoice ID: {alloc_data.invoice_id}")

            # Hardening: Check if allocation exceeds outstanding
            outstanding = await self.get_invoice_outstanding(invoice.id)
            if Decimal(str(alloc_data.allocated_amount)) > outstanding:
                 raise HTTPException(
                     status_code=400,
                     detail=f"Allocation of {alloc_data.allocated_amount} exceeds outstanding amount of {outstanding} for invoice {invoice.invoice_number}"
                 )

            allocation = PaymentAllocation(
                voucher_id=voucher.id,
                invoice_id=alloc_data.invoice_id,
                allocated_amount=alloc_data.allocated_amount
            )
            self.db.add(allocation)
            total_allocated += Decimal(str(alloc_data.allocated_amount))

        if total_allocated > Decimal(str(data.amount)):
            raise HTTPException(status_code=400, detail="Allocated amount exceeds voucher amount")

        await self.db.commit()
        return voucher

    async def get_invoice_outstanding(self, invoice_id: uuid.UUID) -> Decimal:
        invoice = await self.db.get(Invoice, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Sum allocations
        stmt = select(func.sum(PaymentAllocation.allocated_amount)).where(PaymentAllocation.invoice_id == invoice_id)
        res = await self.db.execute(stmt)
        paid = res.scalar() or Decimal("0.00")

        return Decimal(str(invoice.total_amount)) - Decimal(str(paid))

    async def import_bank_statement(self, company_id: uuid.UUID, user_id: uuid.UUID, data: BankStatementCreate) -> BankStatement:
        statement = BankStatement(
            company_id=company_id,
            bank_ledger_id=data.bank_ledger_id,
            statement_date=data.statement_date,
            opening_balance=data.opening_balance,
            closing_balance=data.closing_balance,
            notes=data.notes,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(statement)
        await self.db.flush()

        for line_data in data.lines:
            line = BankStatementLine(
                statement_id=statement.id,
                **line_data.model_dump()
            )
            self.db.add(line)

        await self.db.commit()
        await self.db.refresh(statement, ["lines"])
        return statement

    async def reconcile_line(self, line_id: uuid.UUID, voucher_id: uuid.UUID) -> BankStatementLine:
        line = await self.db.get(BankStatementLine, line_id)
        if not line:
            raise HTTPException(status_code=404, detail="Statement line not found")

        line.voucher_id = voucher_id
        line.is_reconciled = True
        await self.db.commit()
        return line
