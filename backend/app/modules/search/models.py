import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin


class SearchDocument(Base, UUIDMixin):
    __tablename__ = "search_documents"

    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)

    entity_type: Mapped[str] = mapped_column(String(50), index=True) # 'INVOICE', 'PARTY', 'STOCK_ITEM', 'LEDGER', 'VOUCHER'
    entity_id: Mapped[uuid.UUID] = mapped_column(index=True)

    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[str | None] = mapped_column(String(255))

    search_text: Mapped[str] = mapped_column(Text) # Concatenated searchable terms

    url: Mapped[str] = mapped_column(String(500))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
