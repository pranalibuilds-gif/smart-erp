import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin


class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

    entity_type: Mapped[str] = mapped_column(String(50), index=True) # e.g., 'VOUCHER', 'INVOICE', 'PARTY'
    entity_id: Mapped[uuid.UUID | None] = mapped_column(index=True)

    action: Mapped[str] = mapped_column(String(50), index=True) # e.g., 'CREATE', 'POST', 'CANCEL', 'LOGIN'

    old_values: Mapped[dict | None] = mapped_column(JSON)
    new_values: Mapped[dict | None] = mapped_column(JSON)

    ip_address: Mapped[str | None] = mapped_column(String(100))
    user_agent: Mapped[str | None] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("app.modules.auth.models.User")
