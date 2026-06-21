import uuid
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Date, Boolean, Numeric, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin
from app.shared.constants.business import BalanceType, InvitationStatus


class Company(Base, UUIDMixin, AuditMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), index=True)
    legal_name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(500))
    state: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), default="India")

    gst_number: Mapped[str | None] = mapped_column(String(15))
    logo_url: Mapped[str | None] = mapped_column(String(500))

    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    financial_years = relationship("FinancialYear", back_populates="company", cascade="all, delete-orphan")


class FinancialYear(Base, UUIDMixin, AuditMixin):
    __tablename__ = "financial_years"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100)) # e.g., "2025-2026"
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    is_closed: Mapped[bool] = mapped_column(default=False)

    previous_fy_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("financial_years.id", ondelete="SET NULL"))

    # Relationships
    company = relationship("Company", back_populates="financial_years")


class FinancialYearOpeningBalance(Base, UUIDMixin):
    __tablename__ = "fy_opening_balances"

    financial_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_years.id", ondelete="CASCADE"), index=True)
    ledger_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ledgers.id", ondelete="CASCADE"), index=True)

    opening_balance: Mapped[float] = mapped_column(Numeric(15, 2))
    balance_type: Mapped[BalanceType] = mapped_column(Enum(BalanceType))


class FinancialYearStockOpening(Base, UUIDMixin):
    __tablename__ = "fy_stock_openings"

    financial_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_years.id", ondelete="CASCADE"), index=True)
    stock_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stock_items.id", ondelete="CASCADE"), index=True)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"), index=True)

    quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    average_cost: Mapped[float] = mapped_column(Numeric(15, 2))


class CompanyInvitation(Base, UUIDMixin, AuditMixin):
    __tablename__ = "company_invitations"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))

    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus), default=InvitationStatus.PENDING)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    invited_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Relationships
    company = relationship("Company")
    role = relationship("app.modules.auth.models.Role")
    invited_by = relationship("app.modules.auth.models.User")
