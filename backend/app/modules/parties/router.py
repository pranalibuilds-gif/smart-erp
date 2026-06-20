import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company
from app.modules.auth.models import User
from app.modules.companies.models import Company
from .service import PartyService
from .schemas.parties import PartyCreate, PartyUpdate, PartyRead

router = APIRouter(prefix="/parties", tags=["Parties"])


@router.post("", response_model=StandardResponse[PartyRead], status_code=status.HTTP_201_CREATED)
async def create_party(
    data: PartyCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = PartyService(db)
    party = await service.create_party(company.id, current_user.id, data)
    return StandardResponse(success=True, data=PartyRead.model_validate(party), message="Party created successfully")


@router.get("", response_model=StandardResponse[List[PartyRead]])
async def list_parties(
    party_type: str = Query("all", enum=["all", "customer", "supplier", "both"]),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = PartyService(db)
    parties = await service.list_parties(company.id, party_type)
    return StandardResponse(success=True, data=[PartyRead.model_validate(p) for p in parties])


@router.get("/{party_id}", response_model=StandardResponse[PartyRead])
async def get_party(
    party_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = PartyService(db)
    party = await service.get_party(company.id, party_id)
    return StandardResponse(success=True, data=PartyRead.model_validate(party))


@router.patch("/{party_id}", response_model=StandardResponse[PartyRead])
async def update_party(
    party_id: uuid.UUID,
    data: PartyUpdate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = PartyService(db)
    party = await service.update_party(company.id, party_id, current_user.id, data)
    return StandardResponse(success=True, data=PartyRead.model_validate(party))


@router.delete("/{party_id}")
async def delete_party(
    party_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = PartyService(db)
    await service.delete_party(company.id, party_id)
    return StandardResponse(success=True, message="Party deleted successfully")
