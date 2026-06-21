import uuid
from typing import List, Sequence, Optional
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from .models import Voucher, VoucherEntry, VoucherSequence, InventoryTransaction
from .schemas.vouchers import VoucherCreate, VoucherUpdate, InventoryEntryCreate
from app.modules.companies.models import FinancialYear
from app.modules.masters.models import StockItem
from app.modules.audit.service import AuditService
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.business import VoucherType, VoucherStatus


class InventoryPostingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def post_inventory(self, company_id: uuid.UUID, voucher: Voucher, user_id: uuid.UUID):
        # Determine direction based on voucher type
        # PURCHASE, OPENING, ADJ_IN -> Inward (1)
        # SALES, ADJ_OUT -> Outward (-1)
        direction_map = {
            VoucherType.PURCHASE: 1,
            VoucherType.OPENING: 1,
            VoucherType.SALES: -1,
        }
        direction = direction_map.get(voucher.voucher_type, 0)
        if direction == 0:
            return # This voucher type doesn't affect inventory

        for entry in voucher.inventory_entries:
            # 1. Lock StockItem
            stmt = select(StockItem).where(and_(StockItem.id == entry.stock_item_id, StockItem.company_id == company_id)).with_for_update()
            res = await self.db.execute(stmt)
            item = res.scalar_one()

            # 2. Critical Law: No Negative Stock
            new_qty = Decimal(str(item.current_quantity)) + (Decimal(str(entry.quantity)) * direction)
            if new_qty < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Negative stock not allowed for item '{item.name}'. Current: {item.current_quantity}, Requested: {entry.quantity}"
                )

            # 3. Update Average Cost (WAC) for Inward
            if direction == 1:
                # Formula: (Old Qty * Old Avg Cost + Incoming Qty * Incoming Rate) / (Old Qty + Incoming Qty)
                total_value = (Decimal(str(item.current_quantity)) * Decimal(str(item.average_cost))) + (Decimal(str(entry.quantity)) * Decimal(str(entry.rate)))
                if new_qty > 0:
                    item.average_cost = total_value / new_qty

            # 4. Update Quantity Cache
            item.current_quantity = new_qty
            item.updated_by = user_id

    async def reverse_inventory(self, company_id: uuid.UUID, voucher: Voucher, user_id: uuid.UUID):
        direction_map = {
            VoucherType.PURCHASE: 1,
            VoucherType.OPENING: 1,
            VoucherType.SALES: -1,
        }
        direction = direction_map.get(voucher.voucher_type, 0)
        if direction == 0:
            return

        # Reversing is like posting with opposite direction
        reverse_direction = -direction

        for entry in voucher.inventory_entries:
            stmt = select(StockItem).where(and_(StockItem.id == entry.stock_item_id, StockItem.company_id == company_id)).with_for_update()
            res = await self.db.execute(stmt)
            item = res.scalar_one()

            new_qty = Decimal(str(item.current_quantity)) + (Decimal(str(entry.quantity)) * reverse_direction)

            if direction == 1: # Original was inward, reversal is outward-like
                 current_val = Decimal(str(item.current_quantity)) * Decimal(str(item.average_cost))
                 entry_val = Decimal(str(entry.quantity)) * Decimal(str(entry.rate))
                 if new_qty > 0:
                     item.average_cost = (current_val - entry_val) / new_qty

            item.current_quantity = new_qty
            item.updated_by = user_id


class VoucherService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.voucher_repo = SQLAlchemyRepository(db, Voucher)
        self.audit_service = AuditService(db)

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

        fy_code = fy.name
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

        # Law 4: Company Isolation
        # Check ledgers
        from app.modules.masters.models import Ledger
        ledger_ids = [e.ledger_id for e in data.entries]
        stmt = select(Ledger.id).where(and_(Ledger.company_id == company_id, Ledger.id.in_(ledger_ids)))
        res = await self.db.execute(stmt)
        found_ledger_ids = [r for r in res.scalars().all()]
        if len(found_ledger_ids) != len(set(ledger_ids)):
            raise HTTPException(status_code=400, detail="One or more ledgers are invalid or belong to another company")

        # Check stock items
        if data.inventory_entries:
            item_ids = [e.stock_item_id for e in data.inventory_entries]
            stmt = select(StockItem.id).where(and_(StockItem.company_id == company_id, StockItem.id.in_(item_ids)))
            res = await self.db.execute(stmt)
            found_item_ids = [r for r in res.scalars().all()]
            if len(found_item_ids) != len(set(item_ids)):
                 raise HTTPException(status_code=400, detail="One or more stock items are invalid or belong to another company")

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
                **entry_data.model_dump(),
                created_by=user_id,
                updated_by=user_id
            )
            self.db.add(entry)

        # Handle inventory entries
        direction_map = {
            VoucherType.PURCHASE: 1,
            VoucherType.OPENING: 1,
            VoucherType.SALES: -1,
        }
        direction = direction_map.get(data.voucher_type, 0)

        for inv_data in data.inventory_entries:
            inv_entry = InventoryTransaction(
                voucher_id=voucher.id,
                stock_item_id=inv_data.stock_item_id,
                quantity=inv_data.quantity,
                rate=inv_data.rate,
                amount=inv_data.quantity * inv_data.rate,
                direction=direction,
                created_by=user_id,
                updated_by=user_id
            )
            self.db.add(inv_entry)

        await self.db.commit()
        await self.db.refresh(voucher, ["entries", "inventory_entries"])

        # Log action
        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="VOUCHER",
            entity_id=voucher.id,
            action="CANCEL",
            new_values={"status": "CANCELLED"}
        )
        await self.db.commit()

        return voucher

    async def list_vouchers(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> Sequence[Voucher]:
        stmt = select(Voucher).where(
            and_(Voucher.company_id == company_id, Voucher.financial_year_id == fy_id)
        ).options(
            selectinload(Voucher.entries),
            selectinload(Voucher.inventory_entries)
        ).order_by(Voucher.voucher_date.desc(), Voucher.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID) -> Voucher:
        stmt = select(Voucher).where(
            and_(Voucher.id == voucher_id, Voucher.company_id == company_id)
        ).options(
            selectinload(Voucher.entries),
            selectinload(Voucher.inventory_entries)
        )
        result = await self.db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
        return voucher

    async def post_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID, user_id: uuid.UUID) -> Voucher:
        # Load voucher
        voucher = await self.get_voucher(company_id, voucher_id)

        if voucher.status != VoucherStatus.DRAFT:
            raise HTTPException(status_code=400, detail=f"Cannot post voucher in {voucher.status} status")

        # Law 1: Double Entry Validation
        total_debit = sum(Decimal(str(e.debit_amount)) for e in voucher.entries)
        total_credit = sum(Decimal(str(e.credit_amount)) for e in voucher.entries)

        if abs(total_debit - total_credit) > Decimal("0.001"):
            raise HTTPException(status_code=400, detail=f"Voucher is not balanced. Total Dr: {total_debit}, Total Cr: {total_credit}")

        # Law 2: Minimum Entries
        if len(voucher.entries) < 2:
            raise HTTPException(status_code=400, detail="A posted voucher must contain at least 2 entries")

        # Atomic Posting Start
        voucher.status = VoucherStatus.POSTED
        voucher.updated_by = user_id

        # 1. Update Ledger Snapshots (Accounting Integration)
        from app.modules.masters.models import Ledger
        for entry in voucher.entries:
            stmt = select(Ledger).where(Ledger.id == entry.ledger_id).with_for_update()
            res = await self.db.execute(stmt)
            ledger = res.scalar_one()
            ledger.current_balance = Decimal(str(ledger.current_balance)) + (Decimal(str(entry.debit_amount)) - Decimal(str(entry.credit_amount)))
            ledger.updated_by = user_id

        # 2. Update Stock Snapshots (Inventory Integration)
        inv_service = InventoryPostingService(self.db)
        await inv_service.post_inventory(company_id, voucher, user_id)

        await self.db.commit()
        await self.db.refresh(voucher, ["entries", "inventory_entries"])

        # Log action
        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="VOUCHER",
            entity_id=voucher.id,
            action="CANCEL",
            new_values={"status": "CANCELLED"}
        )
        await self.db.commit()

        return voucher

    async def cancel_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID, user_id: uuid.UUID) -> Voucher:
        voucher = await self.get_voucher(company_id, voucher_id)

        if voucher.status == VoucherStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Voucher is already cancelled")

        # Atomic Reversal Start
        if voucher.status == VoucherStatus.POSTED:
            # 1. Reverse Ledger Snapshot effects
            from app.modules.masters.models import Ledger
            for entry in voucher.entries:
                stmt = select(Ledger).where(Ledger.id == entry.ledger_id).with_for_update()
                res = await self.db.execute(stmt)
                ledger = res.scalar_one()
                ledger.current_balance = Decimal(str(ledger.current_balance)) - (Decimal(str(entry.debit_amount)) - Decimal(str(entry.credit_amount)))
                ledger.updated_by = user_id

            # 2. Reverse Inventory Snapshot effects
            inv_service = InventoryPostingService(self.db)
            await inv_service.reverse_inventory(company_id, voucher, user_id)

        voucher.status = VoucherStatus.CANCELLED
        voucher.updated_by = user_id

        await self.db.commit()
        await self.db.refresh(voucher, ["entries", "inventory_entries"])

        # Log action
        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="VOUCHER",
            entity_id=voucher.id,
            action="CANCEL",
            new_values={"status": "CANCELLED"}
        )
        await self.db.commit()

        return voucher
