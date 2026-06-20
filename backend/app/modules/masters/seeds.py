import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from .models import AccountGroup, Ledger, Unit
from app.shared.constants.business import AccountNature, BalanceType

async def seed_company_defaults(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID):
    # 1. Seed Groups
    groups_data = [
        {"name": "Assets", "nature": AccountNature.ASSET, "is_primary": True},
        {"name": "Liabilities", "nature": AccountNature.LIABILITY, "is_primary": True},
        {"name": "Income", "nature": AccountNature.INCOME, "is_primary": True},
        {"name": "Expenses", "nature": AccountNature.EXPENSE, "is_primary": True},
    ]

    groups = {}
    for g in groups_data:
        group = AccountGroup(
            company_id=company_id,
            name=g["name"],
            nature=g["nature"],
            is_primary=g["is_primary"],
            is_system=True,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(group)
        groups[g["name"]] = group

    await db.flush()

    # 2. Seed Ledgers
    ledgers_data = [
        {"name": "Cash", "group": "Assets", "type": BalanceType.DEBIT},
        {"name": "Bank", "group": "Assets", "type": BalanceType.DEBIT},
        {"name": "Sales", "group": "Income", "type": BalanceType.CREDIT},
        {"name": "Purchase", "group": "Expenses", "type": BalanceType.DEBIT},
    ]

    for l in ledgers_data:
        ledger = Ledger(
            company_id=company_id,
            group_id=groups[l["group"]].id,
            name=l["name"],
            opening_balance_type=l["type"],
            is_system=True,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(ledger)

    # 3. Seed Units
    units_data = [
        {"name": "PCS", "description": "Pieces"},
        {"name": "KG", "description": "Kilograms"},
        {"name": "LTR", "description": "Liters"},
        {"name": "BOX", "description": "Boxes"},
    ]

    for u in units_data:
        unit = Unit(
            company_id=company_id,
            name=u["name"],
            description=u["description"],
            is_system=True,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(unit)

    await db.flush()
