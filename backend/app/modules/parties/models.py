import uuid
from sqlalchemy import String, ForeignKey, Boolean, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin


class Party(Base, UUIDMixin, AuditMixin):
    __tablename__ = "parties"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    ledger_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ledgers.id", ondelete="RESTRICT"), unique=True)

    name: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))

    mobile: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))

    gstin: Mapped[str | None] = mapped_column(String(15))
    pan: Mapped[str | None] = mapped_column(String(10))

    address: Mapped[str | None] = mapped_column(String(500))

    credit_limit: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)

    is_customer: Mapped[bool] = mapped_column(default=True)
    is_supplier: Mapped[bool] = mapped_column(default=False)

    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    ledger = relationship("app.modules.masters.models.Ledger")

    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_party_name_per_company"),
        # UniqueConstraint("company_id", "gstin", name="uq_party_gstin_per_company"), # Handled manually if not null
    )
