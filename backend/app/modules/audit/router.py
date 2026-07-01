import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_company, PermissionRequired
from app.modules.companies.models import Company
from .service import AuditService
from .schemas.audit import AuditLogRead
from .models import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get(
    "/logs",
    response_model=StandardResponse[List[AuditLogRead]],
    dependencies=[Depends(PermissionRequired("audit:view"))]
)
async def get_audit_logs(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(100),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    # Use direct query to include user info for the response
    stmt = select(AuditLog).where(AuditLog.company_id == company.id).options(joinedload(AuditLog.user))

    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(AuditLog.entity_id == entity_id)

    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    # Map to schema and include user full name
    data = []
    for log in logs:
        read_log = AuditLogRead.model_validate(log)
        if log.user:
            read_log.user_full_name = log.user.full_name
        data.append(read_log)

    return StandardResponse(success=True, data=data)
