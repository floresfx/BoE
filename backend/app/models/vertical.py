from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Vertical(Base, UUIDMixin, TimestampMixin):
    """Verticales de negocio (global).

    Los verticales definen a qué se dedica cada empresa.
    """
    __tablename__ = "verticals"

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Relaciones existentes
    tenants = relationship("Tenant", back_populates="vertical")

    # Relaciones nuevas (Bloque 2)
    attributes = relationship(
        "VerticalAttribute", back_populates="vertical"
    )