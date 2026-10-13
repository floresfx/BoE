from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class State(Base, UUIDMixin, TimestampMixin):
    """Estados/provincias (global)."""
    __tablename__ = "states"
    __table_args__ = (
        UniqueConstraint("country_id", "code", name="uq_state_country_code"),
    )

    country_id: Mapped[UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    country = relationship("Country", back_populates="states")