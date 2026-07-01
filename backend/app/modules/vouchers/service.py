import uuid
import logging
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
from app.modules.masters.models import StockItem, Warehouse, StockBalance
from app.modules.audit.service import AuditService
from app.modules.notifications.service import NotificationService
from app.modules.search.service import SearchService
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.business import VoucherType, VoucherStatus

logger = logging.getLogger(__name__)


class InventoryPostingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)

    async def post_inventory(self, company_id: uuid.UUID, voucher: Voucher, user_id: uuid.UUID):
        # We process all inventory entries in the voucher.
        # Each entry has its own 'direction' (In/Out) stored during creation.
        if not voucher.inventory_entries:
            return

        # Hardening: Sort and lock Items and Balances deterministically
        all_item_ids = list(set(e.stock_item_id for e in voucher.inventory_entries))
        stmt_items = select(StockItem).where(and_(StockItem.id.in_(all_item_ids), StockItem.company_id == company_id)).order_by(StockItem.id).with_for_update()
        res_items = await self.db.execute(stmt_items)
        items_map = {i.id: i for i in res_items.scalars().all()}

        # Lock Balances (Item + Warehouse)
        balance_keys = list(set((e.stock_item_id, e.warehouse_id) for e in voucher.inventory_entries))
        # SQL IN with tuples is tricky, we'll sort and lock one by one or use OR
        # Given small number of entries per voucher, one-by-one in SORTED order is safe.
        sorted_keys = sorted(balance_keys)

        balances_map = {}
        for item_id, wh_id in sorted_keys:
            stmt_bal = select(StockBalance).where(
                and_(StockBalance.warehouse_id == wh_id, StockBalance.stock_item_id == item_id)
            ).with_for_update()
            res_bal = await self.db.execute(stmt_bal)
            balance = res_bal.scalar_one_or_none()
            if not balance:
                balance = StockBalance(
                    warehouse_id=wh_id,
                    stock_item_id=item_id,
                    quantity=0.00,
                    average_cost=0.00,
                    created_by=user_id,
                    updated_by=user_id
                )
                self.db.add(balance)
            balances_map[(item_id, wh_id)] = balance

        for entry in voucher.inventory_entries:
            item = items_map[entry.stock_item_id]
            balance = balances_map[(entry.stock_item_id, entry.warehouse_id)]
            direction = entry.direction

            if direction == 0: continue

            # 2. Critical Law: No Negative Stock (on warehouse level)
            new_wh_qty = Decimal(str(balance.quantity)) + (Decimal(str(entry.quantity)) * direction)
            if new_wh_qty < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Negative stock not allowed in warehouse for item '{item.name}'. Current: {balance.quantity}, Requested: {entry.quantity}"
                )

            # 3. Update Average Cost (WAC) for Inward
            if direction == 1:
                # Per warehouse WAC
                total_value = (Decimal(str(balance.quantity)) * Decimal(str(balance.average_cost))) + (Decimal(str(entry.quantity)) * Decimal(str(entry.rate)))
                if new_wh_qty > 0:
                    balance.average_cost = total_value / new_wh_qty

                # Company-wide WAC
                new_total_qty = Decimal(str(item.current_quantity)) + Decimal(str(entry.quantity))
                total_company_value = (Decimal(str(item.current_quantity)) * Decimal(str(item.average_cost))) + (Decimal(str(entry.quantity)) * Decimal(str(entry.rate)))
                if new_total_qty > 0:
                    item.average_cost = total_company_value / new_total_qty

            # 4. Update Quantity Cache
            balance.quantity = new_wh_qty
            balance.updated_by = user_id

            item.current_quantity = Decimal(str(item.current_quantity)) + (Decimal(str(entry.quantity)) * direction)
            item.updated_by = user_id

            # Trigger: Low Stock
            if item.current_quantity <= item.reorder_level:
                await self.notification_service.publish_event(
                    company_id=company_id,
                    event_type="stock.low",
                    entity_type="STOCK_ITEM",
                    entity_id=item.id,
                    payload={"item_name": item.name, "current_quantity": float(item.current_quantity)}
                )

    async def reverse_inventory(self, company_id: uuid.UUID, voucher: Voucher, user_id: uuid.UUID):
        if not voucher.inventory_entries:
            return

        # Hardening: Sort entries to prevent deadlocks
        sorted_entries = sorted(voucher.inventory_entries, key=lambda e: (e.stock_item_id, e.warehouse_id))

        for entry in sorted_entries:
            direction = entry.direction
            if direction == 0: continue

            # Reversing is like posting with opposite direction
            reverse_direction = -direction

            # 1. Lock StockItem and StockBalance
            stmt_item = select(StockItem).where(and_(StockItem.id == entry.stock_item_id, StockItem.company_id == company_id)).with_for_update()
            res_item = await self.db.execute(stmt_item)
            item = res_item.scalar_one()

            stmt_bal = select(StockBalance).where(
                and_(StockBalance.warehouse_id == entry.warehouse_id, StockBalance.stock_item_id == entry.stock_item_id)
            ).with_for_update()
            res_bal = await self.db.execute(stmt_bal)
            balance = res_bal.scalar_one()

            new_wh_qty = Decimal(str(balance.quantity)) + (Decimal(str(entry.quantity)) * reverse_direction)

            if direction == 1: # Original was inward, reversal is outward-like
                 current_val = Decimal(str(balance.quantity)) * Decimal(str(balance.average_cost))
                 entry_val = Decimal(str(entry.quantity)) * Decimal(str(entry.rate))
                 if new_wh_qty > 0:
                     balance.average_cost = (current_val - entry_val) / new_wh_qty

                 # Company wide reversal
                 current_company_val = Decimal(str(item.current_quantity)) * Decimal(str(item.average_cost))
                 new_company_qty = Decimal(str(item.current_quantity)) - Decimal(str(entry.quantity))
                 if new_company_qty > 0:
                      item.average_cost = (current_company_val - entry_val) / new_company_qty

            balance.quantity = new_wh_qty
            balance.updated_by = user_id

            item.current_quantity = Decimal(str(item.current_quantity)) + (Decimal(str(entry.quantity)) * reverse_direction)
            item.updated_by = user_id


class VoucherService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.voucher_repo = SQLAlchemyRepository(db, Voucher)
        self.audit_service = AuditService(db)
        self.search_service = SearchService(db)

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
            try:
                async with self.db.begin_nested():
                    seq = VoucherSequence(
                        company_id=company_id,
                        financial_year_id=fy.id,
                        voucher_type=v_type,
                        last_serial=0
                    )
                    self.db.add(seq)
                    await self.db.flush()
            except Exception:
                # Someone else created it in the meantime, fetch it again with lock
                result = await self.db.execute(stmt)
                seq = result.scalar_one()

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
        self, company_id: uuid.UUID, fy: FinancialYear, user_id: uuid.UUID, data: VoucherCreate, commit: bool = True
    ) -> Voucher:
        # 1. Validation: Balance Dr/Cr
        total_debit = sum(Decimal(str(e.debit_amount)) for e in data.entries)
        total_credit = sum(Decimal(str(e.credit_amount)) for e in data.entries)
        if abs(total_debit - total_credit) > 0.01:
            raise HTTPException(status_code=400, detail="Voucher must be balanced (Total Debit must equal Total Credit)")

        # 2. Validation: At least 2 entries
        if len(data.entries) < 2:
            raise HTTPException(status_code=400, detail="Voucher must contain at least 2 accounting entries")

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

            # Check warehouses
            warehouse_ids = [e.warehouse_id for e in data.inventory_entries]
            stmt = select(Warehouse.id).where(and_(Warehouse.company_id == company_id, Warehouse.id.in_(warehouse_ids)))
            res = await self.db.execute(stmt)
            found_wh_ids = [r for r in res.scalars().all()]
            if len(found_wh_ids) != len(set(warehouse_ids)):
                 raise HTTPException(status_code=400, detail="One or more warehouses are invalid or belong to another company")

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
        voucher_direction = direction_map.get(data.voucher_type, 0)

        for inv_data in data.inventory_entries:
            # Entry-specific direction overrides voucher-type direction
            entry_direction = inv_data.direction if inv_data.direction is not None else voucher_direction

            inv_entry = InventoryTransaction(
                voucher_id=voucher.id,
                warehouse_id=inv_data.warehouse_id,
                stock_item_id=inv_data.stock_item_id,
                quantity=inv_data.quantity,
                rate=inv_data.rate,
                amount=inv_data.quantity * inv_data.rate,
                direction=entry_direction,
                created_by=user_id,
                updated_by=user_id
            )
            self.db.add(inv_entry)

        await self.db.flush()

        # Log action
        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="VOUCHER",
            entity_id=voucher.id,
            action="CREATE",
            new_values={"status": "DRAFT"}
        )

        if commit:
            await self.db.commit()
            await self.db.refresh(voucher, ["entries", "inventory_entries"])

        return voucher

    async def list_vouchers(self, company_id: uuid.UUID, fy_id: uuid.UUID) -> Sequence[Voucher]:
        stmt = select(Voucher).where(
            and_(Voucher.company_id == company_id, Voucher.financial_year_id == fy_id)
        ).options(
            selectinload(Voucher.entries).joinedload(VoucherEntry.ledger),
            selectinload(Voucher.inventory_entries).joinedload(InventoryTransaction.stock_item)
        ).order_by(Voucher.voucher_date.desc(), Voucher.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID, for_update: bool = False) -> Voucher:
        stmt = select(Voucher).where(
            and_(Voucher.id == voucher_id, Voucher.company_id == company_id)
        ).options(
            selectinload(Voucher.entries),
            selectinload(Voucher.inventory_entries)
        )
        if for_update:
            stmt = stmt.with_for_update()

        result = await self.db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
        return voucher

    async def post_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID, user_id: uuid.UUID, commit: bool = True) -> Voucher:
        # Load voucher with lock to prevent concurrent posting of SAME voucher
        voucher = await self.get_voucher(company_id, voucher_id, for_update=True)

        # Hardening: Lock FinancialYear row to prevent concurrent closing of FY
        stmt_fy = select(FinancialYear).where(FinancialYear.id == voucher.financial_year_id).with_for_update()
        res_fy = await self.db.execute(stmt_fy)
        fy = res_fy.scalar_one()

        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

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
        # Hardening: Sort and Lock ALL required ledgers in one query to prevent deadlocks
        all_ledger_ids = list(set(e.ledger_id for e in voucher.entries))
        stmt = select(Ledger).where(Ledger.id.in_(all_ledger_ids)).order_by(Ledger.id).with_for_update()
        res = await self.db.execute(stmt)
        ledgers_map = {l.id: l for l in res.scalars().all()}

        for entry in voucher.entries:
            ledger = ledgers_map[entry.ledger_id]
            ledger.current_balance = Decimal(str(ledger.current_balance)) + (Decimal(str(entry.debit_amount)) - Decimal(str(entry.credit_amount)))
            ledger.updated_by = user_id

        # 2. Update Stock Snapshots (Inventory Integration)
        inv_service = InventoryPostingService(self.db)
        await inv_service.post_inventory(company_id, voucher, user_id)

        await self.db.flush()

        # Log action
        try:
            await self.audit_service.log_action(
                user_id=user_id,
                company_id=company_id,
                entity_type="VOUCHER",
                entity_id=voucher.id,
                action="POST",
                new_values={"status": "POSTED"}
            )
        except Exception as e:
            logger.warning(f"Soft-fail: Audit logging failed during voucher post: {e}")

        # Index
        try:
            await self.search_service.update_index(
                company_id=company_id,
                entity_type="VOUCHER",
                entity_id=voucher.id,
                title=voucher.voucher_number,
                subtitle=f"{voucher.voucher_type} Voucher",
                search_terms=[voucher.voucher_number, voucher.narration or ""],
                url=f"/vouchers/{voucher.id}"
            )
        except Exception as e:
            logger.warning(f"Soft-fail: Search indexing failed during voucher post: {e}")

        if commit:
            await self.db.commit()
            await self.db.refresh(voucher, ["entries", "inventory_entries"])

        return voucher

    async def cancel_voucher(self, company_id: uuid.UUID, voucher_id: uuid.UUID, user_id: uuid.UUID, commit: bool = True) -> Voucher:
        # Load voucher with lock to prevent concurrent cancellation
        voucher = await self.get_voucher(company_id, voucher_id, for_update=True)

        # Hardening: Lock FinancialYear row to prevent concurrent closing of FY
        stmt_fy = select(FinancialYear).where(FinancialYear.id == voucher.financial_year_id).with_for_update()
        res_fy = await self.db.execute(stmt_fy)
        fy = res_fy.scalar_one()

        if fy.is_closed:
            raise HTTPException(status_code=400, detail="Financial Year is closed")

        if voucher.status == VoucherStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Voucher is already cancelled")

        # Atomic Reversal Start
        if voucher.status == VoucherStatus.POSTED:
            # 1. Reverse Ledger Snapshot effects
            from app.modules.masters.models import Ledger
            # Hardening: Sort and Lock ALL required ledgers in one query to prevent deadlocks
            all_ledger_ids = list(set(e.ledger_id for e in voucher.entries))
            stmt = select(Ledger).where(Ledger.id.in_(all_ledger_ids)).order_by(Ledger.id).with_for_update()
            res = await self.db.execute(stmt)
            ledgers_map = {l.id: l for l in res.scalars().all()}

            for entry in voucher.entries:
                ledger = ledgers_map[entry.ledger_id]
                ledger.current_balance = Decimal(str(ledger.current_balance)) - (Decimal(str(entry.debit_amount)) - Decimal(str(entry.credit_amount)))
                ledger.updated_by = user_id

            # 2. Reverse Inventory Snapshot effects
            inv_service = InventoryPostingService(self.db)
            await inv_service.reverse_inventory(company_id, voucher, user_id)

        voucher.status = VoucherStatus.CANCELLED
        voucher.updated_by = user_id

        await self.db.flush()

        # Log action
        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="VOUCHER",
            entity_id=voucher.id,
            action="CANCEL",
            new_values={"status": "CANCELLED"}
        )
        # Index
        await self.search_service.update_index(
            company_id=company_id,
            entity_type="VOUCHER",
            entity_id=voucher.id,
            title=voucher.voucher_number,
            subtitle=f"{voucher.voucher_type} Voucher",
            search_terms=[voucher.voucher_number, voucher.narration or ""],
            url=f"/vouchers/{voucher.id}"
        )

        if commit:
            await self.db.commit()
            await self.db.refresh(voucher, ["entries", "inventory_entries"])

        return voucher
