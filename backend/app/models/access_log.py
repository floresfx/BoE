from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AccessLog(Base, UUIDMixin, TimestampMixin):
    """Registro de accesos."""
    __tablename__ = "access_logs"
    __table_args__ = (
        Index("ix_access_log_user_created", "user_id", "created_at"),
        Index("ix_access_log_tenant_created", "tenant_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id"), nullable=False
    )
    event: Mapped[str] = mapped_column(String(50), nullable=False)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relaciones
    user = relationship("User", back_populates="access_logs")