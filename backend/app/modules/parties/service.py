import uuid
from typing import List, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from fastapi import HTTPException

from .models import Party
from .schemas.parties import PartyCreate, PartyUpdate
from app.modules.masters.models import Ledger, AccountGroup
from app.modules.audit.service import AuditService
from app.modules.search.service import SearchService
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.business import BalanceType


class PartyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.party_repo = SQLAlchemyRepository(db, Party)
        self.ledger_repo = SQLAlchemyRepository(db, Ledger)
        self.group_repo = SQLAlchemyRepository(db, AccountGroup)
        self.audit_service = AuditService(db)
        self.search_service = SearchService(db)

    async def create_party(self, company_id: uuid.UUID, user_id: uuid.UUID, data: PartyCreate) -> Party:
        # Check if party name exists
        existing = await self.db.execute(
            select(Party).where(and_(Party.company_id == company_id, Party.name == data.name))
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Party name already exists")

        # 1. Determine Ledger Group
        group_name = "Sundry Debtors" if data.is_customer else "Sundry Creditors"
        group_stmt = select(AccountGroup).where(and_(AccountGroup.company_id == company_id, AccountGroup.name == group_name))
        group_res = await self.db.execute(group_stmt)
        group = group_res.scalar_one_or_none()

        if not group:
             raise HTTPException(status_code=400, detail=f"Required account group '{group_name}' not found. Please ensure company is properly initialized.")

        # 2. Create Ledger
        ledger = Ledger(
            company_id=company_id,
            group_id=group.id,
            name=data.name,
            opening_balance=0.00, # Initial
            opening_balance_type=BalanceType.DEBIT if data.is_customer else BalanceType.CREDIT,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(ledger)
        await self.db.flush()

        # 3. Create Party
        party = Party(
            **data.model_dump(),
            company_id=company_id,
            ledger_id=ledger.id,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(party)

        try:
            await self.db.commit()
            await self.db.refresh(party)

            # Log action
            await self.audit_service.log_action(
                user_id=user_id,
                company_id=company_id,
                entity_type="PARTY",
                entity_id=party.id,
                action="CREATE",
                new_values={"name": party.name, "ledger_id": str(ledger.id)}
            )
            # Index
            await self.search_service.update_index(
                company_id=company_id,
                entity_type="PARTY",
                entity_id=party.id,
                title=party.name,
                subtitle="Customer" if party.is_customer else "Supplier",
                search_terms=[party.name, party.email or "", party.gst_number or ""],
                url=f"/parties/{party.id}"
            )

            await self.db.commit()

            return party
        except Exception as e:
            await self.db.rollback()
            raise e

    async def list_parties(self, company_id: uuid.UUID, party_type: str = "all") -> Sequence[Party]:
        stmt = select(Party).where(Party.company_id == company_id)

        if party_type == "customer":
            stmt = stmt.where(Party.is_customer == True)
        elif party_type == "supplier":
            stmt = stmt.where(Party.is_supplier == True)
        elif party_type == "both":
            stmt = stmt.where(and_(Party.is_customer == True, Party.is_supplier == True))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_party(self, company_id: uuid.UUID, party_id: uuid.UUID) -> Party:
        party = await self.party_repo.get(party_id)
        if not party or party.company_id != company_id:
            raise HTTPException(status_code=404, detail="Party not found")
        return party

    async def update_party(self, company_id: uuid.UUID, party_id: uuid.UUID, user_id: uuid.UUID, data: PartyUpdate) -> Party:
        party = await self.get_party(company_id, party_id)

        # Update ledger name if name changes
        if data.name and data.name != party.name:
            ledger = await self.ledger_repo.get(party.ledger_id)
            if ledger:
                ledger.name = data.name
                ledger.updated_by = user_id

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(party, field, value)

        party.updated_by = user_id
        await self.db.commit()
        await self.db.refresh(party)
        return party

    async def delete_party(self, company_id: uuid.UUID, party_id: uuid.UUID):
        party = await self.get_party(company_id, party_id)

        # Check for transactions (TODO: implement when vouchers exist)

        await self.db.delete(party)
        await self.db.commit()
