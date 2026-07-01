import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company, PermissionRequired
from app.modules.auth.models import User
from .service import CompanyService
from .fy_service import FinancialYearService
from .team_service import TeamService
from .schemas import CompanyCreate, CompanyRead, FinancialYearRead, CompanyUpdate
from .schemas.team import CompanyInvitationCreate, CompanyInvitationRead, CompanyMemberRead

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", response_model=StandardResponse[CompanyRead], status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)
    company = await service.create_company(current_user.id, data)
    return StandardResponse(
        success=True,
        data=CompanyRead.model_validate(company),
        message="Company created successfully"
    )


@router.get("", response_model=StandardResponse[List[CompanyRead]])
async def list_user_companies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)
    companies = await service.get_user_companies(current_user.id)
    return StandardResponse(
        success=True,
        data=[CompanyRead.model_validate(c) for c in companies],
        message="User companies retrieved successfully"
    )


@router.get(
    "/{company_id}",
    response_model=StandardResponse[CompanyRead],
    dependencies=[Depends(PermissionRequired("company:view"))]
)
async def get_company(
    company_id: uuid.UUID,
    authorized_company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    if company_id != authorized_company.id:
        raise HTTPException(status_code=403, detail="Company ID mismatch")

    return StandardResponse(
        success=True,
        data=CompanyRead.model_validate(authorized_company),
        message="Company retrieved successfully"
    )


@router.put(
    "/{company_id}",
    response_model=StandardResponse[CompanyRead],
    dependencies=[Depends(PermissionRequired("company:manage"))]
)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    authorized_company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    if company_id != authorized_company.id:
        raise HTTPException(status_code=403, detail="Company ID mismatch")

    service = CompanyService(db)
    company = await service.update_company(authorized_company.id, current_user.id, data)
    return StandardResponse(
        success=True,
        data=CompanyRead.model_validate(company),
        message="Company updated successfully"
    )

@router.get(
    "/{company_id}/financial-years",
    response_model=StandardResponse[List[FinancialYearRead]],
    dependencies=[Depends(PermissionRequired("company:view"))]
)
async def list_financial_years(
    company_id: uuid.UUID,
    authorized_company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    if company_id != authorized_company.id:
        raise HTTPException(status_code=403, detail="Company ID mismatch")

    from sqlalchemy import select
    from .models import FinancialYear

    stmt = select(FinancialYear).where(FinancialYear.company_id == authorized_company.id)
    result = await db.execute(stmt)
    years = result.scalars().all()

    return StandardResponse(
        success=True,
        data=[FinancialYearRead.model_validate(y) for y in years],
        message="Financial years retrieved successfully"
    )


@router.post(
    "/{company_id}/financial-years/{fy_id}/close",
    response_model=StandardResponse[FinancialYearRead],
    dependencies=[Depends(PermissionRequired("company:manage"))]
)
async def close_financial_year(
    company_id: uuid.UUID,
    fy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    authorized_company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    if company_id != authorized_company.id:
        raise HTTPException(status_code=403, detail="Company ID mismatch")

    service = FinancialYearService(db)
    fy = await service.close_and_rollover(authorized_company.id, fy_id, current_user.id)
    return StandardResponse(
        success=True,
        data=FinancialYearRead.model_validate(fy),
        message="Financial year closed successfully and next year created"
    )


# --- Team Management ---

@router.get(
    "/{company_id}/members",
    response_model=StandardResponse[List[CompanyMemberRead]],
    dependencies=[Depends(PermissionRequired("team:view"))]
)
async def list_company_members(
    company_id: uuid.UUID,
    authorized_company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    if company_id != authorized_company.id:
        raise HTTPException(status_code=403, detail="Company ID mismatch")

    service = TeamService(db)
    members = await service.get_members(authorized_company.id)
    return StandardResponse(success=True, data=members)


@router.post(
    "/{company_id}/invite",
    response_model=StandardResponse[dict],
    dependencies=[Depends(PermissionRequired("team:invite"))]
)
async def invite_user(
    company_id: uuid.UUID,
    data: CompanyInvitationCreate,
    current_user: User = Depends(get_current_user),
    authorized_company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    if company_id != authorized_company.id:
        raise HTTPException(status_code=403, detail="Company ID mismatch")

    service = TeamService(db)
    invitation, token = await service.invite_user(authorized_company.id, current_user.id, data)
    # In a real app, we would email the token
    return StandardResponse(success=True, data={"invitation_id": str(invitation.id), "token": token}, message="Invitation created")


@router.get(
    "/{company_id}/invitations",
    response_model=StandardResponse[List[CompanyInvitationRead]],
    dependencies=[Depends(PermissionRequired("team:view"))]
)
async def list_invitations(
    company_id: uuid.UUID,
    authorized_company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    if company_id != authorized_company.id:
        raise HTTPException(status_code=403, detail="Company ID mismatch")

    service = TeamService(db)
    invites = await service.get_invitations(authorized_company.id)

    data = []
    for invite in invites:
        read = CompanyInvitationRead.model_validate(invite)
        if invite.role: read.role_name = invite.role.name
        if invite.invited_by: read.invited_by_name = invite.invited_by.full_name
        data.append(read)

    return StandardResponse(success=True, data=data)


@router.post("/invitations/accept")
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TeamService(db)
    await service.accept_invitation(token, current_user.id)
    return StandardResponse(success=True, message="Invitation accepted")
