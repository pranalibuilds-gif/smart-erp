from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.shared.database.session import get_db
from app.modules.auth.models import User, UserCompanyRole, Role
from app.modules.companies.models import Company
from .current_user import get_current_user
from .current_company import get_current_company

async def get_current_company_role(
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
) -> Role | None:
    """
    Returns the user\u0027s role in the active company.
    Superusers return None (as they bypass role checks).
    """
    if current_user.is_superuser:
        return None

    stmt = (
        select(Role)
        .join(UserCompanyRole)
        .where(
            UserCompanyRole.user_id == current_user.id,
            UserCompanyRole.company_id == company.id
        )
        .options(selectinload(Role.permissions))
    )
    result = await db.execute(stmt)
    role = result.scalars().first()

    if not role:
        # This shouldn\u0027t happen if get_current_company passed for non-superusers,
        # but handled for safety.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not found for this company"
        )

    return role
