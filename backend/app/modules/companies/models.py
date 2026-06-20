from sqlalchemy.orm import Mapped, mapped_column
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin


class Company(Base, UUIDMixin, AuditMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Financial data (optional initially)
    address: Mapped[str | None] = mapped_column()
    gstin: Mapped[str | None] = mapped_column()
