import uuid
from datetime import date
from sqlalchemy import String, ForeignKey, Date, Enum, Numeric, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin
from app.shared.constants.business import VoucherType, VoucherStatus


class Voucher(Base, UUIDMixin, AuditMixin):
    __tablename__ = "vouchers"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    financial_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_years.id", ondelete="RESTRICT"), index=True)

    voucher_type: Mapped[VoucherType] = mapped_column(Enum(VoucherType), index=True)
    voucher_number: Mapped[str] = mapped_column(String(100), index=True)

    voucher_date: Mapped[date] = mapped_column(Date, default=date.today)

    status: Mapped[VoucherStatus] = mapped_column(Enum(VoucherStatus), default=VoucherStatus.DRAFT)

    narration: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    entries = relationship("VoucherEntry", back_populates="voucher", cascade="all, delete-orphan")
    inventory_entries = relationship("InventoryTransaction", back_populates="voucher", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("company_id", "financial_year_id", "voucher_type", "voucher_number", name="uq_voucher_number"),
    )


class VoucherEntry(Base, UUIDMixin, AuditMixin):
    __tablename__ = "voucher_entries"

    voucher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vouchers.id", ondelete="CASCADE"), index=True)
    ledger_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ledgers.id", ondelete="RESTRICT"), index=True)

    debit_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)
    credit_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)

    narration: Mapped[str | None] = mapped_column(String(500))

    # Relationships
    voucher = relationship("Voucher", back_populates="entries")
    ledger = relationship("app.modules.masters.models.Ledger")


class InventoryTransaction(Base, UUIDMixin, AuditMixin):
    __tablename__ = "inventory_transactions"

    voucher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vouchers.id", ondelete="CASCADE"), index=True)
    stock_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stock_items.id", ondelete="RESTRICT"), index=True)

    quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    rate: Mapped[float] = mapped_column(Numeric(15, 2))
    amount: Mapped[float] = mapped_column(Numeric(15, 2))

    # 1 for Inward (Purchase/Receipt), -1 for Outward (Sales/Issue)
    direction: Mapped[int] = mapped_column(Integer)

    # Relationships
    voucher = relationship("Voucher", back_populates="inventory_entries")
    stock_item = relationship("app.modules.masters.models.StockItem")


class VoucherSequence(Base):
    """Internal model to track the last serial number for vouchers."""
    __tablename__ = "voucher_sequences"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True)
    financial_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_years.id", ondelete="CASCADE"), primary_key=True)
    voucher_type: Mapped[VoucherType] = mapped_column(Enum(VoucherType), primary_key=True)

    last_serial: Mapped[int] = mapped_column(Integer, default=0)
