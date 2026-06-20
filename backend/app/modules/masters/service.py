import uuid
from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from .models import AccountGroup, Ledger, Unit, StockGroup, StockItem
from .schemas.account_groups import AccountGroupCreate, AccountGroupUpdate
from .schemas.ledgers import LedgerCreate, LedgerUpdate
from .schemas.units import UnitCreate, UnitUpdate
from .schemas.stock_groups import StockGroupCreate, StockGroupUpdate
from .schemas.stock_items import StockItemCreate, StockItemUpdate
from app.shared.database.repository import SQLAlchemyRepository


class MastersService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.group_repo = SQLAlchemyRepository(db, AccountGroup)
        self.ledger_repo = SQLAlchemyRepository(db, Ledger)
        self.unit_repo = SQLAlchemyRepository(db, Unit)
        self.stock_group_repo = SQLAlchemyRepository(db, StockGroup)
        self.stock_item_repo = SQLAlchemyRepository(db, StockItem)

    # --- Account Groups ---

    async def create_account_group(self, company_id: uuid.UUID, user_id: uuid.UUID, data: AccountGroupCreate) -> AccountGroup:
        # Rules:
        # 2. Parent and child must belong to same company
        if data.parent_id:
            parent = await self.group_repo.get(data.parent_id)
            if not parent or parent.company_id != company_id:
                raise HTTPException(status_code=400, detail="Invalid parent group")
            # Inheritance of nature if not provided
            if not data.nature:
                data.nature = parent.nature

        # 4. Root groups cannot have parents (handled by UI/logic)

        group = AccountGroup(
            **data.model_dump(),
            company_id=company_id,
            created_by=user_id,
            updated_by=user_id
        )
        return await self.group_repo.create(group)

    async def get_account_groups(self, company_id: uuid.UUID, root_only: bool = False) -> Sequence[AccountGroup]:
        stmt = select(AccountGroup).where(AccountGroup.company_id == company_id)
        if root_only:
            stmt = stmt.where(AccountGroup.parent_id == None)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_account_group(self, company_id: uuid.UUID, group_id: uuid.UUID, user_id: uuid.UUID, data: AccountGroupUpdate) -> AccountGroup:
        group = await self.group_repo.get(group_id)
        if not group or group.company_id != company_id:
            raise HTTPException(status_code=404, detail="Account group not found")

        if group.is_system:
             # Basic update might be allowed but nature/is_system shouldn't usually change
             pass

        # 5. Circular references prohibited
        if data.parent_id:
            if data.parent_id == group_id:
                raise HTTPException(status_code=400, detail="A group cannot be its own parent")

            # Check for deeper circularity
            curr_parent_id = data.parent_id
            while curr_parent_id:
                p = await self.group_repo.get(curr_parent_id)
                if not p: break
                if p.parent_id == group_id:
                    raise HTTPException(status_code=400, detail="Circular reference detected")
                curr_parent_id = p.parent_id

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(group, field, value)

        group.updated_by = user_id
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete_account_group(self, company_id: uuid.UUID, group_id: uuid.UUID):
        group = await self.group_repo.get(group_id)
        if not group or group.company_id != company_id:
            raise HTTPException(status_code=404, detail="Account group not found")

        # 3. System groups cannot be deleted
        if group.is_system:
            raise HTTPException(status_code=400, detail="System groups cannot be deleted")

        # Check for children or ledgers
        # ...

        await self.db.delete(group)
        await self.db.commit()

    # --- Ledgers ---

    async def create_ledger(self, company_id: uuid.UUID, user_id: uuid.UUID, data: LedgerCreate) -> Ledger:
        # Validate group
        group = await self.group_repo.get(data.group_id)
        if not group or group.company_id != company_id:
            raise HTTPException(status_code=400, detail="Invalid account group")

        ledger = Ledger(
            **data.model_dump(),
            company_id=company_id,
            current_balance=data.opening_balance, # Initial cache
            created_by=user_id,
            updated_by=user_id
        )
        # TODO: Option B - Create Opening Voucher

        return await self.ledger_repo.create(ledger)

    async def get_ledgers(self, company_id: uuid.UUID) -> Sequence[Ledger]:
        stmt = select(Ledger).where(Ledger.company_id == company_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_ledger(self, company_id: uuid.UUID, ledger_id: uuid.UUID, user_id: uuid.UUID, data: LedgerUpdate) -> Ledger:
        ledger = await self.ledger_repo.get(ledger_id)
        if not ledger or ledger.company_id != company_id:
            raise HTTPException(status_code=404, detail="Ledger not found")

        if ledger.is_system and data.name:
             # System ledgers might have restricted name updates
             pass

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ledger, field, value)

        ledger.updated_by = user_id
        await self.db.commit()
        await self.db.refresh(ledger)
        return ledger

    # --- Units ---

    async def create_unit(self, company_id: uuid.UUID, user_id: uuid.UUID, data: UnitCreate) -> Unit:
        unit = Unit(
            **data.model_dump(),
            company_id=company_id,
            created_by=user_id,
            updated_by=user_id
        )
        return await self.unit_repo.create(unit)

    async def get_units(self, company_id: uuid.UUID) -> Sequence[Unit]:
        stmt = select(Unit).where(Unit.company_id == company_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_unit(self, company_id: uuid.UUID, unit_id: uuid.UUID, user_id: uuid.UUID, data: UnitUpdate) -> Unit:
        unit = await self.unit_repo.get(unit_id)
        if not unit or unit.company_id != company_id:
            raise HTTPException(status_code=404, detail="Unit not found")

        if unit.is_system:
            raise HTTPException(status_code=400, detail="System units cannot be updated")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(unit, field, value)

        unit.updated_by = user_id
        await self.db.commit()
        await self.db.refresh(unit)
        return unit

    async def delete_unit(self, company_id: uuid.UUID, unit_id: uuid.UUID):
        unit = await self.unit_repo.get(unit_id)
        if not unit or unit.company_id != company_id:
            raise HTTPException(status_code=404, detail="Unit not found")

        if unit.is_system:
            raise HTTPException(status_code=400, detail="System units cannot be deleted")

        await self.db.delete(unit)
        await self.db.commit()

    # --- Stock Groups ---

    async def create_stock_group(self, company_id: uuid.UUID, user_id: uuid.UUID, data: StockGroupCreate) -> StockGroup:
        if data.parent_id:
            parent = await self.stock_group_repo.get(data.parent_id)
            if not parent or parent.company_id != company_id:
                raise HTTPException(status_code=400, detail="Invalid parent stock group")

        group = StockGroup(
            **data.model_dump(),
            company_id=company_id,
            created_by=user_id,
            updated_by=user_id
        )
        return await self.stock_group_repo.create(group)

    async def get_stock_groups(self, company_id: uuid.UUID, root_only: bool = False) -> Sequence[StockGroup]:
        stmt = select(StockGroup).where(StockGroup.company_id == company_id)
        if root_only:
            stmt = stmt.where(StockGroup.parent_id == None)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # --- Stock Items ---

    async def create_stock_item(self, company_id: uuid.UUID, user_id: uuid.UUID, data: StockItemCreate) -> StockItem:
        # Validate unit
        unit = await self.unit_repo.get(data.unit_id)
        if not unit or unit.company_id != company_id:
            raise HTTPException(status_code=400, detail="Invalid unit")

        # Validate stock group
        if data.stock_group_id:
            group = await self.stock_group_repo.get(data.stock_group_id)
            if not group or group.company_id != company_id:
                raise HTTPException(status_code=400, detail="Invalid stock group")

        # Validate SKU uniqueness per company
        if data.sku:
            existing = await self.db.execute(
                select(StockItem).where(and_(StockItem.company_id == company_id, StockItem.sku == data.sku))
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="SKU already exists for this company")

        item = StockItem(
            **data.model_dump(),
            company_id=company_id,
            created_by=user_id,
            updated_by=user_id
        )
        return await self.stock_item_repo.create(item)

    async def get_stock_items(self, company_id: uuid.UUID) -> Sequence[StockItem]:
        stmt = select(StockItem).where(StockItem.company_id == company_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
