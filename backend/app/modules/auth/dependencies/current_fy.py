import uuid
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.session import get_db
from app.modules.companies.models import Company, FinancialYear
from .current_company import get_current_company

async def get_current_financial_year(
    x_financial_year_id: uuid.UUID | None = Header(None, alias="X-Financial-Year-ID"),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
) -> FinancialYear:
    """
    Extracts and validates the current financial year for the active company.
    If no ID is provided in header, it can either return the latest open year
    or raise an error depending on strictness. Here we will be strict.
    """
    if not x_financial_year_id:
        # Fallback: find the latest open financial year for this company
        stmt = select(FinancialYear).where(
            FinancialYear.company_id == company.id,
            FinancialYear.is_closed == False
        ).order_by(FinancialYear.start_date.desc())

        result = await db.execute(stmt)
        fy = result.scalars().first()

        if not fy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active financial year found for this company. Please provide X-Financial-Year-ID."
            )
        return fy

    # Verify provided FY belongs to the company
    stmt = select(FinancialYear).where(
        FinancialYear.id == x_financial_year_id,
        FinancialYear.company_id == company.id
    )
    result = await db.execute(stmt)
    fy = result.scalars().first()

    if not fy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid financial year for this company"
        )

    return fy
