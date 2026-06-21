import uuid
from sqlalchemy import String, ForeignKey, Boolean, Numeric, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin
from app.shared.constants.business import AccountNature, BalanceType, ItemType, LedgerType


class AccountGroup(Base, UUIDMixin, AuditMixin):
    __tablename__ = "account_groups"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str | None] = mapped_column(String(50), index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("account_groups.id", ondelete="SET NULL"))

    is_primary: Mapped[bool] = mapped_column(default=False)
    nature: Mapped[AccountNature | None] = mapped_column(Enum(AccountNature))
    is_system: Mapped[bool] = mapped_column(default=False)

    # Relationships
    parent = relationship("AccountGroup", remote_side="AccountGroup.id", backref="subgroups")


class Ledger(Base, UUIDMixin, AuditMixin):
    __tablename__ = "ledgers"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account_groups.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str | None] = mapped_column(String(50), index=True)

    opening_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)
    opening_balance_type: Mapped[BalanceType] = mapped_column(Enum(BalanceType), default=BalanceType.DEBIT)
    current_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)

    ledger_type: Mapped[LedgerType] = mapped_column(Enum(LedgerType), default=LedgerType.GENERAL)

    is_system: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    group = relationship("AccountGroup")


class Unit(Base, UUIDMixin, AuditMixin):
    __tablename__ = "units"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(50)) # e.g., "PCS", "KG"
    description: Mapped[str | None] = mapped_column(String(100))
    is_system: Mapped[bool] = mapped_column(default=False)


class StockGroup(Base, UUIDMixin, AuditMixin):
    __tablename__ = "stock_groups"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("stock_groups.id", ondelete="SET NULL"))

    # Relationships
    parent = relationship("StockGroup", remote_side="StockGroup.id", backref="subgroups")


class StockItem(Base, UUIDMixin, AuditMixin):
    __tablename__ = "stock_items"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    stock_group_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("stock_groups.id", ondelete="SET NULL"), index=True)
    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id", ondelete="RESTRICT"), index=True)

    name: Mapped[str] = mapped_column(String(255), index=True)
    sku: Mapped[str | None] = mapped_column(String(100), index=True)

    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), default=ItemType.PRODUCT)

    current_quantity: Mapped[float] = mapped_column(Numeric(15, 3), default=0.00)
    average_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)

    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    stock_group = relationship("StockGroup")
    unit = relationship("Unit")


class Warehouse(Base, UUIDMixin, AuditMixin):
    __tablename__ = "warehouses"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    address: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_warehouse_code_per_company"),
        UniqueConstraint("company_id", "name", name="uq_warehouse_name_per_company"),
    )


class StockBalance(Base, UUIDMixin, AuditMixin):
    __tablename__ = "stock_balances"

    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"), index=True)
    stock_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stock_items.id", ondelete="CASCADE"), index=True)

    quantity: Mapped[float] = mapped_column(Numeric(15, 3), default=0.00)
    average_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)

    __table_args__ = (
        UniqueConstraint("warehouse_id", "stock_item_id", name="uq_stock_balance_per_warehouse"),
    )
