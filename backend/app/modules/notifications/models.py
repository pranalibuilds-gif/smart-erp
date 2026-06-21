import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin


class DomainEvent(Base, UUIDMixin):
    """
    Audit log of all internal business events.
    Not for users, but for system processing.
    """
    __tablename__ = "domain_events"

    company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True) # e.g. 'stock.low', 'invoice.posted'

    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(index=True)

    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Notification(Base, UUIDMixin):
    """
    In-app notifications for users.
    """
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String(1000))

    is_read: Mapped[bool] = mapped_column(default=False, index=True)

    event_type: Mapped[str | None] = mapped_column(String(100)) # Link back to source event type
    entity_id: Mapped[uuid.UUID | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserNotificationPreference(Base, UUIDMixin):
    """
    Control which event types a user wants to be notified about.
    """
    __tablename__ = "user_notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)

    event_type: Mapped[str] = mapped_column(String(100))
    is_enabled: Mapped[bool] = mapped_column(default=True)

    # Relationships
    user = relationship("app.modules.auth.models.User")
