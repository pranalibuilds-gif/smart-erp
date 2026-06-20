import uuid
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.session import get_db
from app.modules.auth.models import User, UserCompanyRole
from app.modules.companies.models import Company
from .current_user import get_current_user

async def get_current_company(
    x_company_id: uuid.UUID = Header(..., alias="X-Company-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Company:
    """
    Validates that the company exists and the user is a member.
    """
    # 1. Superuser override (can access any company)
    # But we still need to verify company exists

    # 2. Fetch Company
    result = await db.execute(select(Company).where(Company.id == x_company_id))
    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID"
        )

    if current_user.is_superuser:
        return company

    # 3. Check membership
    stmt = select(UserCompanyRole).where(
        UserCompanyRole.user_id == current_user.id,
        UserCompanyRole.company_id == x_company_id
    )
    res = await db.execute(stmt)
    membership = res.scalars().first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this company"
        )

    return company
