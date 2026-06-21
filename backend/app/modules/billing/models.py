import uuid
from datetime import date
from sqlalchemy import String, ForeignKey, Date, Enum, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin
from app.shared.constants.business import DocumentType, InvoiceStatus


class Invoice(Base, UUIDMixin, AuditMixin):
    __tablename__ = "invoices"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    financial_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_years.id", ondelete="RESTRICT"), index=True)

    party_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parties.id", ondelete="RESTRICT"), index=True)
    voucher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vouchers.id", ondelete="SET NULL"), unique=True)

    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), index=True)
    invoice_number: Mapped[str] = mapped_column(String(100), index=True)
    invoice_date: Mapped[date] = mapped_column(Date, default=date.today)

    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)

    taxable_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)

    narration: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    party = relationship("app.modules.parties.models.Party")
    voucher = relationship("app.modules.vouchers.models.Voucher")


class InvoiceItem(Base, UUIDMixin):
    __tablename__ = "invoice_items"

    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), index=True)
    stock_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("stock_items.id", ondelete="SET NULL"), index=True)
    warehouse_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("warehouses.id", ondelete="SET NULL"), index=True)

    # Snapshots for immutability
    item_name: Mapped[str] = mapped_column(String(255))
    item_code: Mapped[str | None] = mapped_column(String(100))
    unit_name: Mapped[str | None] = mapped_column(String(50))
    hsn_code: Mapped[str | None] = mapped_column(String(20))

    quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    rate: Mapped[float] = mapped_column(Numeric(15, 2))
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00)

    taxable_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2))

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
