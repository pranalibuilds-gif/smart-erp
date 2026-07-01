import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company, PermissionRequired
from app.modules.auth.models import User
from app.modules.companies.models import Company
from .service import NotificationService
from .schemas.notifications import NotificationRead

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=StandardResponse[List[NotificationRead]],
    dependencies=[Depends(PermissionRequired("notification:view"))]
)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    items = await service.get_user_notifications(current_user.id, company.id)
    return StandardResponse(success=True, data=[NotificationRead.model_validate(i) for i in items])


@router.post(
    "/{notification_id}/read",
    response_model=StandardResponse[None],
    dependencies=[Depends(PermissionRequired("notification:update"))]
)
async def mark_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    await service.mark_as_read(notification_id, current_user.id)
    return StandardResponse(success=True, message="Marked as read")


@router.post(
    "/read-all",
    response_model=StandardResponse[None],
    dependencies=[Depends(PermissionRequired("notification:update"))]
)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    await service.mark_all_as_read(current_user.id, company.id)
    return StandardResponse(success=True, message="All marked as read")
