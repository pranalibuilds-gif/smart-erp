import uuid
from datetime import datetime, date, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slugify import slugify

from .models import Company, FinancialYear
from .schemas import CompanyCreate, CompanyUpdate
from app.modules.auth.models import UserCompanyRole, Role, Permission
from app.modules.masters.seeds import seed_company_defaults
from app.shared.database.repository import SQLAlchemyRepository
from app.shared.constants.permissions import ALL_PERMISSIONS


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SQLAlchemyRepository(db, Company)
        self.fy_repo = SQLAlchemyRepository(db, FinancialYear)

    async def create_company(self, user_id: uuid.UUID, data: CompanyCreate) -> Company:
        # 1. Create Company
        slug = slugify(data.name)
        # Check for slug uniqueness
        existing = await self.db.execute(select(Company).where(Company.slug == slug))
        if existing.scalar_one_or_none():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        company = Company(
            name=data.name,
            legal_name=data.legal_name,
            slug=slug,
            email=data.email,
            phone=data.phone,
            address=data.address,
            state=data.state,
            country=data.country,
            gst_number=data.gst_number,
            logo_url=data.logo_url,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(company)
        await self.db.flush() # Get company.id

        # 2. Create Financial Year
        # Default FY name: "2025-2026" if start_date is in 2025
        fy_name = f"{data.financial_year_start.year}-{data.financial_year_start.year + 1}"
        # End date is usually 1 year - 1 day after start date
        end_date = date(data.financial_year_start.year + 1, 3, 31) if data.financial_year_start.month == 4 else data.financial_year_start + timedelta(days=364)

        financial_year = FinancialYear(
            company_id=company.id,
            name=fy_name,
            start_date=data.financial_year_start,
            end_date=end_date,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(financial_year)

        # 3. Assign Creator as ADMIN
        # Find ADMIN role
        role_stmt = select(Role).where(Role.name == "ADMIN")
        role_result = await self.db.execute(role_stmt)
        admin_role = role_result.scalar_one_or_none()

        if not admin_role:
            admin_role = Role(name="ADMIN", description="Company Administrator")
            self.db.add(admin_role)
            await self.db.flush()

        # Ensure ADMIN role has all permissions
        for perm_name in ALL_PERMISSIONS:
            perm_stmt = select(Permission).where(Permission.name == perm_name)
            perm_result = await self.db.execute(perm_stmt)
            perm = perm_result.scalar_one_or_none()
            if not perm:
                perm = Permission(name=perm_name)
                self.db.add(perm)
                await self.db.flush()

            if perm not in admin_role.permissions:
                admin_role.permissions.append(perm)

        user_company_role = UserCompanyRole(
            user_id=user_id,
            company_id=company.id,
            role_id=admin_role.id
        )
        self.db.add(user_company_role)

        # 4. Seed Default Data (Groups, Ledgers, Units)
        await seed_company_defaults(self.db, company.id, user_id)

        await self.db.commit()
        await self.db.refresh(company)
        return company

    async def get_user_companies(self, user_id: uuid.UUID) -> List[Company]:
        stmt = select(Company).join(UserCompanyRole).where(UserCompanyRole.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_company(self, company_id: uuid.UUID) -> Company | None:
        return await self.repo.get(company_id)
