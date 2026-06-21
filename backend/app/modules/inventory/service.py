import uuid
from decimal import Decimal
from typing import List, Sequence
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from .models import StockAdjustment, StockAdjustmentItem, StockTransfer, StockTransferItem
from .schemas.adjustments import StockAdjustmentCreate
from .schemas.transfers import StockTransferCreate
from app.modules.companies.models import FinancialYear
from app.modules.masters.models import StockItem, StockBalance, Ledger
from app.modules.vouchers.service import VoucherService, InventoryPostingService
from app.modules.vouchers.schemas.vouchers import VoucherCreate, VoucherEntryCreate, InventoryEntryCreate
from app.modules.audit.service import AuditService
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.business import InvoiceStatus, VoucherType


class StockAdjustmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.adjustment_repo = SQLAlchemyRepository(db, StockAdjustment)
        self.audit_service = AuditService(db)

    async def _generate_adjustment_number(self, company_id: uuid.UUID, fy: FinancialYear) -> str:
        stmt = select(func.count(StockAdjustment.id)).where(
            and_(
                StockAdjustment.company_id == company_id,
                StockAdjustment.financial_year_id == fy.id
            )
        )
        res = await self.db.execute(stmt)
        count = res.scalar() or 0
        return f"ADJ/{fy.name[2:4]}-{fy.name[7:9]}/{(count + 1):06d}"

    async def create_adjustment(self, company_id: uuid.UUID, fy: FinancialYear, user_id: uuid.UUID, data: StockAdjustmentCreate) -> StockAdjustment:
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        adj_no = await self._generate_adjustment_number(company_id, fy)

        adjustment = StockAdjustment(
            company_id=company_id,
            financial_year_id=fy.id,
            warehouse_id=data.warehouse_id,
            adjustment_no=adj_no,
            adjustment_date=data.adjustment_date,
            reason=data.reason,
            notes=data.notes,
            status=InvoiceStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(adjustment)
        await self.db.flush()

        for item_data in data.items:
            # Get current system quantity from StockBalance
            stmt = select(StockBalance).where(
                and_(StockBalance.warehouse_id == data.warehouse_id, StockBalance.stock_item_id == item_data.stock_item_id)
            )
            res = await self.db.execute(stmt)
            balance = res.scalar_one_or_none()
            sys_qty = float(balance.quantity) if balance else 0.0

            # Rate snapshot from StockItem (average cost)
            item_stmt = select(StockItem).where(StockItem.id == item_data.stock_item_id)
            item_res = await self.db.execute(item_stmt)
            stock_item = item_res.scalar_one()

            diff = item_data.physical_quantity - sys_qty

            line = StockAdjustmentItem(
                adjustment_id=adjustment.id,
                stock_item_id=item_data.stock_item_id,
                system_quantity=sys_qty,
                physical_quantity=item_data.physical_quantity,
                difference_quantity=diff,
                rate_snapshot=float(stock_item.average_cost)
            )
            self.db.add(line)

        await self.db.commit()
        await self.db.refresh(adjustment, ["items"])
        return adjustment

    async def list_adjustments(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> Sequence[StockAdjustment]:
        stmt = select(StockAdjustment).where(
            and_(StockAdjustment.company_id == company_id, StockAdjustment.financial_year_id == fy_id)
        ).options(selectinload(StockAdjustment.items)).order_by(StockAdjustment.adjustment_date.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_adjustment(self, company_id: uuid.UUID, adj_id: uuid.UUID) -> StockAdjustment:
        stmt = select(StockAdjustment).where(
            and_(StockAdjustment.id == adj_id, StockAdjustment.company_id == company_id)
        ).options(selectinload(StockAdjustment.items))
        result = await self.db.execute(stmt)
        adj = result.scalar_one_or_none()
        if not adj:
            raise HTTPException(status_code=404, detail="Adjustment not found")
        return adj

    async def post_adjustment(self, company_id: uuid.UUID, adj_id: uuid.UUID, user_id: uuid.UUID) -> StockAdjustment:
        adj = await self.get_adjustment(company_id, adj_id)

        # FY Lock Check
        fy = await self.db.get(FinancialYear, adj.financial_year_id)
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        if adj.status != InvoiceStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Only draft adjustments can be posted")

        # 1. Prepare Accounting entries
        # Gain: Dr Inventory, Cr Gain
        # Loss: Dr Loss, Cr Inventory

        # Find required ledgers
        stmt = select(Ledger).where(and_(Ledger.company_id == company_id, Ledger.name == "Inventory"))
        res = await self.db.execute(stmt)
        inv_ledger = res.scalar_one_or_none()

        stmt = select(Ledger).where(and_(Ledger.company_id == company_id, Ledger.name == "Inventory Adjustment Gain"))
        res = await self.db.execute(stmt)
        gain_ledger = res.scalar_one_or_none()

        stmt = select(Ledger).where(and_(Ledger.company_id == company_id, Ledger.name == "Inventory Adjustment Loss"))
        res = await self.db.execute(stmt)
        loss_ledger = res.scalar_one_or_none()

        if not all([inv_ledger, gain_ledger, loss_ledger]):
             raise HTTPException(status_code=400, detail="Required system ledgers (Inventory, Gain/Loss) not found")

        total_gain_val = Decimal("0.00")
        total_loss_val = Decimal("0.00")

        inventory_entries = []
        for item in adj.items:
            diff = Decimal(str(item.difference_quantity))
            if diff == 0: continue

            val = abs(diff) * Decimal(str(item.rate_snapshot))
            if diff > 0:
                total_gain_val += val
                # Inward transaction
                inventory_entries.append(InventoryEntryCreate(
                    warehouse_id=adj.warehouse_id,
                    stock_item_id=item.stock_item_id,
                    quantity=float(diff),
                    rate=item.rate_snapshot,
                    narration=f"Adj Increase: {adj.adjustment_no}"
                ))
            else:
                total_loss_val += val
                # Outward transaction
                inventory_entries.append(InventoryEntryCreate(
                    warehouse_id=adj.warehouse_id,
                    stock_item_id=item.stock_item_id,
                    quantity=float(abs(diff)),
                    rate=item.rate_snapshot,
                    narration=f"Adj Decrease: {adj.adjustment_no}"
                ))

        # Create Accounting Voucher
        entries = []
        if total_gain_val > 0:
            entries.append(VoucherEntryCreate(ledger_id=inv_ledger.id, debit_amount=float(total_gain_val), credit_amount=0))
            entries.append(VoucherEntryCreate(ledger_id=gain_ledger.id, debit_amount=0, credit_amount=float(total_gain_val)))

        if total_loss_val > 0:
            entries.append(VoucherEntryCreate(ledger_id=loss_ledger.id, debit_amount=float(total_loss_val), credit_amount=0))
            entries.append(VoucherEntryCreate(ledger_id=inv_ledger.id, debit_amount=0, credit_amount=float(total_loss_val)))

        v_service = VoucherService(self.db)
        fy = await self.db.get(FinancialYear, adj.financial_year_id)

        # We need a VoucherType for Adjustments? Decision 1 said "Voucher remains root".
        # I'll use JOURNAL for adjustments or add ADJ type.
        # Let's use JOURNAL for now as it's standard for adjustments.

        v_data = VoucherCreate(
            voucher_type=VoucherType.JOURNAL,
            voucher_date=adj.adjustment_date,
            narration=f"System generated from Stock Adjustment {adj.adjustment_no}",
            entries=entries,
            inventory_entries=inventory_entries
        )

        voucher = await v_service.create_voucher(company_id, fy, user_id, v_data)
        await v_service.post_voucher(company_id, voucher.id, user_id)

        # Update Adjustment status
        adj.status = InvoiceStatus.POSTED
        adj.voucher_id = voucher.id
        adj.updated_by = user_id

        await self.db.commit()

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="STOCK_ADJUSTMENT",
            entity_id=adj.id,
            action="POST",
            new_values={"status": "POSTED", "voucher_id": str(voucher.id)}
        )
        await self.db.commit()

        return adj

    async def cancel_adjustment(self, company_id: uuid.UUID, adj_id: uuid.UUID, user_id: uuid.UUID) -> StockAdjustment:
        adj = await self.get_adjustment(company_id, adj_id)

        # FY Lock Check
        fy = await self.db.get(FinancialYear, adj.financial_year_id)
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        if adj.status == InvoiceStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Already cancelled")

        if adj.status == InvoiceStatus.POSTED and adj.voucher_id:
            v_service = VoucherService(self.db)
            await v_service.cancel_voucher(company_id, adj.voucher_id, user_id)

        adj.status = InvoiceStatus.CANCELLED
        adj.updated_by = user_id

        await self.db.commit()

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="STOCK_ADJUSTMENT",
            entity_id=adj.id,
            action="CANCEL",
            new_values={"status": "CANCELLED"}
        )
        await self.db.commit()

        return adj


class StockTransferService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.transfer_repo = SQLAlchemyRepository(db, StockTransfer)
        self.audit_service = AuditService(db)

    async def _generate_transfer_number(self, company_id: uuid.UUID, fy: FinancialYear) -> str:
        stmt = select(func.count(StockTransfer.id)).where(
            and_(
                StockTransfer.company_id == company_id,
                StockTransfer.financial_year_id == fy.id
            )
        )
        res = await self.db.execute(stmt)
        count = res.scalar() or 0
        return f"TRN/{fy.name[2:4]}-{fy.name[7:9]}/{(count + 1):06d}"

    async def create_transfer(self, company_id: uuid.UUID, fy: FinancialYear, user_id: uuid.UUID, data: StockTransferCreate) -> StockTransfer:
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        if data.from_warehouse_id == data.to_warehouse_id:
             raise HTTPException(status_code=400, detail="Source and destination warehouses cannot be the same")

        trn_no = await self._generate_transfer_number(company_id, fy)

        transfer = StockTransfer(
            company_id=company_id,
            financial_year_id=fy.id,
            from_warehouse_id=data.from_warehouse_id,
            to_warehouse_id=data.to_warehouse_id,
            transfer_no=trn_no,
            transfer_date=data.transfer_date,
            notes=data.notes,
            status=InvoiceStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(transfer)
        await self.db.flush()

        for item_data in data.items:
            item_stmt = select(StockItem).where(StockItem.id == item_data.stock_item_id)
            item_res = await self.db.execute(item_stmt)
            stock_item = item_res.scalar_one()

            line = StockTransferItem(
                transfer_id=transfer.id,
                stock_item_id=item_data.stock_item_id,
                quantity=item_data.quantity,
                rate_snapshot=float(stock_item.average_cost)
            )
            self.db.add(line)

        await self.db.commit()
        await self.db.refresh(transfer, ["items"])
        return transfer

    async def list_transfers(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> Sequence[StockTransfer]:
        stmt = select(StockTransfer).where(
            and_(StockTransfer.company_id == company_id, StockTransfer.financial_year_id == fy_id)
        ).options(selectinload(StockTransfer.items)).order_by(StockTransfer.transfer_date.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_transfer(self, company_id: uuid.UUID, trn_id: uuid.UUID) -> StockTransfer:
        stmt = select(StockTransfer).where(
            and_(StockTransfer.id == trn_id, StockTransfer.company_id == company_id)
        ).options(selectinload(StockTransfer.items))
        result = await self.db.execute(stmt)
        trn = result.scalar_one_or_none()
        if not trn:
            raise HTTPException(status_code=404, detail="Transfer not found")
        return trn

    async def post_transfer(self, company_id: uuid.UUID, trn_id: uuid.UUID, user_id: uuid.UUID) -> StockTransfer:
        trn = await self.get_transfer(company_id, trn_id)

        # FY Lock Check
        fy = await self.db.get(FinancialYear, trn.financial_year_id)
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        if trn.status != InvoiceStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Only draft transfers can be posted")

        # 1. Update StockBalances directly for transfer
        # (Transfers don't affect average cost generally in WAC)
        # (Actually, they might in some systems, but here we assume items move at current cost)

        for line in trn.items:
            # OUT from source
            source_stmt = select(StockBalance).where(
                and_(StockBalance.warehouse_id == trn.from_warehouse_id, StockBalance.stock_item_id == line.stock_item_id)
            ).with_for_update()
            res_s = await self.db.execute(source_stmt)
            source_bal = res_s.scalar_one()

            if source_bal.quantity < line.quantity:
                 raise HTTPException(status_code=400, detail=f"Insufficient stock in source warehouse for item ID {line.stock_item_id}")

            source_bal.quantity -= Decimal(str(line.quantity))

            # IN to destination
            dest_stmt = select(StockBalance).where(
                and_(StockBalance.warehouse_id == trn.to_warehouse_id, StockBalance.stock_item_id == line.stock_item_id)
            ).with_for_update()
            res_d = await self.db.execute(dest_stmt)
            dest_bal = res_d.scalar_one_or_none()

            if not dest_bal:
                dest_bal = StockBalance(
                    warehouse_id=trn.to_warehouse_id,
                    stock_item_id=line.stock_item_id,
                    quantity=0.00,
                    average_cost=line.rate_snapshot, # Use transfer rate
                    created_by=user_id,
                    updated_by=user_id
                )
                self.db.add(dest_bal)

            dest_bal.quantity += Decimal(str(line.quantity))

        trn.status = InvoiceStatus.POSTED
        trn.updated_by = user_id

        await self.db.commit()

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="STOCK_TRANSFER",
            entity_id=trn.id,
            action="POST",
            new_values={"status": "POSTED"}
        )
        await self.db.commit()

        return trn

    async def cancel_transfer(self, company_id: uuid.UUID, trn_id: uuid.UUID, user_id: uuid.UUID) -> StockTransfer:
        trn = await self.get_transfer(company_id, trn_id)

        # FY Lock Check
        fy = await self.db.get(FinancialYear, trn.financial_year_id)
        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        if trn.status != InvoiceStatus.POSTED:
             raise HTTPException(status_code=400, detail="Only posted transfers can be cancelled")

        # Reverse the move
        for line in trn.items:
             # Add back to source
             source_stmt = select(StockBalance).where(
                and_(StockBalance.warehouse_id == trn.from_warehouse_id, StockBalance.stock_item_id == line.stock_item_id)
             ).with_for_update()
             res_s = await self.db.execute(source_stmt)
             source_bal = res_s.scalar_one()
             source_bal.quantity += Decimal(str(line.quantity))

             # Remove from destination
             dest_stmt = select(StockBalance).where(
                and_(StockBalance.warehouse_id == trn.to_warehouse_id, StockBalance.stock_item_id == line.stock_item_id)
             ).with_for_update()
             res_d = await self.db.execute(dest_stmt)
             dest_bal = res_d.scalar_one()
             dest_bal.quantity -= Decimal(str(line.quantity))

        trn.status = InvoiceStatus.CANCELLED
        trn.updated_by = user_id
        await self.db.commit()

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="STOCK_TRANSFER",
            entity_id=trn.id,
            action="CANCEL",
            new_values={"status": "CANCELLED"}
        )
        await self.db.commit()
        return trn
