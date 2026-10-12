from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SecureDevice(Base, UUIDMixin, TimestampMixin):
    """Dispositivos seguros del usuario."""
    __tablename__ = "secure_devices"
    __table_args__ = (
        UniqueConstraint("user_id", "fingerprint", name="uq_device_user_fp"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relaciones
    user = relationship("User", back_populates="secure_devices")