import uuid
from datetime import date
from sqlalchemy import String, ForeignKey, Date, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin
from app.shared.constants.business import InvoiceStatus


class StockAdjustment(Base, UUIDMixin, AuditMixin):
    __tablename__ = "stock_adjustments"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    financial_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_years.id", ondelete="RESTRICT"), index=True)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), index=True)

    adjustment_no: Mapped[str] = mapped_column(String(100), index=True)
    adjustment_date: Mapped[date] = mapped_column(Date, default=date.today)

    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    reason: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(String(1000))

    voucher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vouchers.id", ondelete="SET NULL"), unique=True)

    # Relationships
    items = relationship("StockAdjustmentItem", back_populates="adjustment", cascade="all, delete-orphan")
    warehouse = relationship("app.modules.masters.models.Warehouse")
    voucher = relationship("app.modules.vouchers.models.Voucher")

    __table_args__ = (
        UniqueConstraint("company_id", "financial_year_id", "adjustment_no", name="uq_stock_adjustment_no"),
    )


class StockAdjustmentItem(Base, UUIDMixin):
    __tablename__ = "stock_adjustment_items"

    adjustment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stock_adjustments.id", ondelete="CASCADE"), index=True)
    stock_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stock_items.id", ondelete="RESTRICT"), index=True)

    system_quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    physical_quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    difference_quantity: Mapped[float] = mapped_column(Numeric(15, 3))

    rate_snapshot: Mapped[float] = mapped_column(Numeric(15, 2))

    # Relationships
    adjustment = relationship("StockAdjustment", back_populates="items")
    stock_item = relationship("app.modules.masters.models.StockItem")


class StockTransfer(Base, UUIDMixin, AuditMixin):
    __tablename__ = "stock_transfers"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    financial_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_years.id", ondelete="RESTRICT"), index=True)

    from_warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), index=True)
    to_warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), index=True)

    transfer_no: Mapped[str] = mapped_column(String(100), index=True)
    transfer_date: Mapped[date] = mapped_column(Date, default=date.today)

    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    notes: Mapped[str | None] = mapped_column(String(1000))

    voucher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vouchers.id", ondelete="SET NULL"), unique=True)

    # Relationships
    items = relationship("StockTransferItem", back_populates="transfer", cascade="all, delete-orphan")
    from_warehouse = relationship("app.modules.masters.models.Warehouse", foreign_keys=[from_warehouse_id])
    to_warehouse = relationship("app.modules.masters.models.Warehouse", foreign_keys=[to_warehouse_id])

    __table_args__ = (
        UniqueConstraint("company_id", "financial_year_id", "transfer_no", name="uq_stock_transfer_no"),
    )


class StockTransferItem(Base, UUIDMixin):
    __tablename__ = "stock_transfer_items"

    transfer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stock_transfers.id", ondelete="CASCADE"), index=True)
    stock_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stock_items.id", ondelete="RESTRICT"), index=True)

    quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    rate_snapshot: Mapped[float] = mapped_column(Numeric(15, 2))

    # Relationships
    transfer = relationship("StockTransfer", back_populates="items")
    stock_item = relationship("app.modules.masters.models.StockItem")
