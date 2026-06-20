import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base
from app.shared.database.mixins import UUIDMixin, AuditMixin


class RolePermission(Base):
    """Association table between Roles and Permissions."""
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )


class UserCompanyRole(Base):
    """
    Contextual RBAC: Links Users to Companies with specific Roles.
    Allows a User to have multiple roles in the same company.
    """
    __tablename__ = "user_company_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", "role_id", name="uq_user_company_role"),
    )


class Permission(Base, UUIDMixin, AuditMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255))


class Role(Base, UUIDMixin, AuditMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    permissions = relationship("Permission", secondary="role_permissions", backref="roles")


class User(Base, UUIDMixin, AuditMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)


class RefreshToken(Base, UUIDMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
