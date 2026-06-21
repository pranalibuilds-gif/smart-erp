import uuid
from datetime import date
from sqlalchemy import String, ForeignKey, Date, Enum, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin
from app.shared.constants.business import ChequeStatus


class BankAccount(Base, UUIDMixin, AuditMixin):
    __tablename__ = "bank_accounts"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    ledger_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ledgers.id", ondelete="RESTRICT"), unique=True)

    account_name: Mapped[str] = mapped_column(String(255))
    account_number: Mapped[str] = mapped_column(String(100), index=True)
    bank_name: Mapped[str] = mapped_column(String(255))
    ifsc_code: Mapped[str | None] = mapped_column(String(20))
    branch_name: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    ledger = relationship("app.modules.masters.models.Ledger")


class PaymentAllocation(Base, UUIDMixin):
    """Links a Payment/Receipt Voucher to one or more Invoices."""
    __tablename__ = "payment_allocations"

    voucher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vouchers.id", ondelete="CASCADE"), index=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), index=True)

    allocated_amount: Mapped[float] = mapped_column(Numeric(15, 2))

    # Relationships
    voucher = relationship("app.modules.vouchers.models.Voucher")
    invoice = relationship("app.modules.billing.models.Invoice")


class BankStatement(Base, UUIDMixin, AuditMixin):
    __tablename__ = "bank_statements"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    bank_ledger_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ledgers.id", ondelete="RESTRICT"), index=True)

    statement_date: Mapped[date] = mapped_column(Date)
    opening_balance: Mapped[float] = mapped_column(Numeric(15, 2))
    closing_balance: Mapped[float] = mapped_column(Numeric(15, 2))

    notes: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    lines = relationship("BankStatementLine", back_populates="statement", cascade="all, delete-orphan")
    bank_ledger = relationship("app.modules.masters.models.Ledger")


class BankStatementLine(Base, UUIDMixin):
    __tablename__ = "bank_statement_lines"

    statement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bank_statements.id", ondelete="CASCADE"), index=True)

    txn_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(500))
    reference: Mapped[str | None] = mapped_column(String(100))

    # Positive for credit (received), negative for debit (paid)
    amount: Mapped[float] = mapped_column(Numeric(15, 2))

    is_reconciled: Mapped[bool] = mapped_column(default=False)
    voucher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vouchers.id", ondelete="SET NULL"))

    # Relationships
    statement = relationship("BankStatement", back_populates="lines")
    voucher = relationship("app.modules.vouchers.models.Voucher")
