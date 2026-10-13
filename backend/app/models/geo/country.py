from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Country(Base, UUIDMixin, TimestampMixin):
    """Paises (global)."""
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(
        String(2), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone_id: Mapped[UUID] = mapped_column(
        ForeignKey("timezones.id"), nullable=False
    )
    currency_id: Mapped[UUID] = mapped_column(
        ForeignKey("currencies.id"), nullable=False
    )
    phone_prefix: Mapped[str] = mapped_column(String(5), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    timezone = relationship("Timezone")
    currency = relationship("Currency")
    states = relationship("State", back_populates="country")
    cities = relationship("City", back_populates="country")