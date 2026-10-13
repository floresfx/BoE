from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class City(Base, UUIDMixin, TimestampMixin):
    """Ciudades (global)."""
    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint(
            "country_id", "state_id", "name", name="uq_city_country_state_name"
        ),
    )

    country_id: Mapped[UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False, index=True
    )
    state_id: Mapped[UUID] = mapped_column(
        ForeignKey("states.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    country = relationship("Country", back_populates="cities")