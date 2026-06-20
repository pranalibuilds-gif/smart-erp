import uuid
from typing import List, Sequence, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException

from .models import Voucher, VoucherEntry, VoucherSequence
from .schemas.vouchers import VoucherCreate, VoucherUpdate
from app.modules.companies.models import FinancialYear
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.business import VoucherType, VoucherStatus


class VoucherService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.voucher_repo = SQLAlchemyRepository(db, Voucher)

    async def _generate_voucher_number(
        self, company_id: uuid.UUID, fy: FinancialYear, v_type: VoucherType
    ) -> str:
        # Get or create sequence
        stmt = select(VoucherSequence).where(
            and_(
                VoucherSequence.company_id == company_id,
                VoucherSequence.financial_year_id == fy.id,
                VoucherSequence.voucher_type == v_type
            )
        ).with_for_update() # Lock for numbering integrity

        result = await self.db.execute(stmt)
        seq = result.scalar_one_or_none()

        if not seq:
            seq = VoucherSequence(
                company_id=company_id,
                financial_year_id=fy.id,
                voucher_type=v_type,
                last_serial=0
            )
            self.db.add(seq)

        seq.last_serial += 1

        # Format TYPE/FY/SERIAL
        # TYPE code (3 chars)
        type_codes = {
            VoucherType.SALES: "SAL",
            VoucherType.PURCHASE: "PUR",
            VoucherType.PAYMENT: "PAY",
            VoucherType.RECEIPT: "REC",
            VoucherType.JOURNAL: "JRN",
            VoucherType.CONTRA: "CON",
            VoucherType.OPENING: "OPN",
        }
        type_code = type_codes.get(v_type, v_type.value[:3])

        # FY code from name e.g. "2025-2026" -> "25-26"
        fy_code = fy.name # Use as is if it's already "25-26", otherwise format
        if len(fy_code) == 9 and fy_code[4] == '-':
             fy_code = f"{fy_code[2:4]}-{fy_code[7:9]}"

        serial = str(seq.last_serial).zfill(6)

        return f"{type_code}/{fy_code}/{serial}"

    async def create_voucher(
        self, company_id: uuid.UUID, fy: FinancialYear, user_id: uuid.UUID, data: VoucherCreate
    ) -> Voucher:
        # Law 3: Financial Year Lock
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        # Law 4: Company Isolation (Refs must belong to same company)
        # Check ledgers
        from app.modules.masters.models import Ledger
        ledger_ids = [e.ledger_id for e in data.entries]
        stmt = select(Ledger.id).where(and_(Ledger.company_id == company_id, Ledger.id.in_(ledger_ids)))
        res = await self.db.execute(stmt)
        found_ledger_ids = [r for r in res.scalars().all()]
        if len(found_ledger_ids) != len(set(ledger_ids)):
            raise HTTPException(status_code=400, detail="One or more ledgers are invalid or belong to another company")

        # Law 1 & 2: Double Entry & Min entries (Validated in schema but double check for min entries if needed)
        # For Phase 5A we just create. Phase 5B will validate Dr=Cr on POST.

        # Generate number
        v_number = await self._generate_voucher_number(company_id, fy, data.voucher_type)

        voucher = Voucher(
            company_id=company_id,
            financial_year_id=fy.id,
            voucher_type=data.voucher_type,
            voucher_number=v_number,
            voucher_date=data.voucher_date,
            narration=data.narration,
            status=VoucherStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(voucher)
        await self.db.flush()

        for entry_data in data.entries:
            entry = VoucherEntry(
                voucher_id=voucher.id,
                **entry_data.model_dump()
            )
            self.db.add(entry)

        await self.db.commit()
        await self.db.refresh(voucher)
        # Load entries
        stmt = select(Voucher).where(Voucher.id == voucher.id).options(
            # relationship loading handled by relationship definitions usually,
            # but let's be explicit if needed or just use refresh
        )
        return voucher

    async def list_vouchers(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> Sequence[Voucher]:
        stmt = select(Voucher).where(
            and_(Voucher.company_id == company_id, Voucher.financial_year_id == fy_id)
        ).order_by(Voucher.voucher_date.desc(), Voucher.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID) -> Voucher:
        stmt = select(Voucher).where(and_(Voucher.id == voucher_id, Voucher.company_id == company_id))
        result = await self.db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
        return voucher

    async def post_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID, user_id: uuid.UUID) -> Voucher:
        voucher = await self.get_voucher(company_id, voucher_id)

        if voucher.status != VoucherStatus.DRAFT:
            raise HTTPException(status_code=400, detail=f"Cannot post voucher in {voucher.status} status")

        # Law 1: Double Entry Validation
        total_debit = sum(e.debit_amount for e in voucher.entries)
        total_credit = sum(e.credit_amount for e in voucher.entries)

        if abs(total_debit - total_credit) > 0.001: # Handle precision
            raise HTTPException(status_code=400, detail=f"Voucher is not balanced. Total Dr: {total_debit}, Total Cr: {total_credit}")

        # Law 2: Minimum Entries
        if len(voucher.entries) < 2:
            raise HTTPException(status_code=400, detail="A posted voucher must contain at least 2 entries")

        # Atomic Posting Start
        voucher.status = VoucherStatus.POSTED
        voucher.updated_by = user_id

        # Update Ledger Snapshots
        from app.modules.masters.models import Ledger
        for entry in voucher.entries:
            stmt = select(Ledger).where(Ledger.id == entry.ledger_id).with_for_update()
            res = await self.db.execute(stmt)
            ledger = res.scalar_one()
            ledger.current_balance += (entry.debit_amount - entry.credit_amount)
            ledger.updated_by = user_id

        await self.db.commit()
        await self.db.refresh(voucher)
        return voucher

    async def cancel_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID, user_id: uuid.UUID) -> Voucher:
        voucher = await self.get_voucher(company_id, voucher_id)

        if voucher.status == VoucherStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Voucher is already cancelled")

        # If it was posted, we need to reverse effects in snapshots
        if voucher.status == VoucherStatus.POSTED:
            from app.modules.masters.models import Ledger
            for entry in voucher.entries:
                stmt = select(Ledger).where(Ledger.id == entry.ledger_id).with_for_update()
                res = await self.db.execute(stmt)
                ledger = res.scalar_one()
                ledger.current_balance -= (entry.debit_amount - entry.credit_amount)
                ledger.updated_by = user_id

        voucher.status = VoucherStatus.CANCELLED
        voucher.updated_by = user_id

        await self.db.commit()
        await self.db.refresh(voucher)
        return voucher
