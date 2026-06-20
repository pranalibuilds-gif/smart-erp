import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr


def get_utc_now():
    """Returns current UTC time."""
    return datetime.now(timezone.utc)


def get_uuid():
    """Generates a UUID version 4."""
    return uuid.uuid4()


class UUIDMixin:
    """Mixin that adds a UUID primary key to a model."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=get_uuid,
        sort_order=-100 # Ensure ID stays at the top of the table
    )


class AuditMixin:
    """Mixin that adds standard audit fields to a model."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        server_default=func.now()
    )

    # Nullable UUIDs for actor tracking
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class CompanyMixin:
    """
    Mixin that adds company isolation to a model.
    Used for master data and transactional entities.
    """
    @declared_attr
    def company_id(self) -> Mapped[uuid.UUID]:
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("companies.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        )
