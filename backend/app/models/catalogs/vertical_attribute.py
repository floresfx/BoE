from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class VerticalAttribute(Base, UUIDMixin, TimestampMixin):
    """Relación N:M entre verticales y atributos."""
    __tablename__ = "verticals_attributes"
    __table_args__ = (
        UniqueConstraint(
            "vertical_id", "attribute_id", name="uq_vertical_attr"
        ),
    )

    vertical_id: Mapped[UUID] = mapped_column(
        ForeignKey("verticals.id"), nullable=False, index=True
    )
    attribute_id: Mapped[UUID] = mapped_column(
        ForeignKey("attributes.id"), nullable=False, index=True
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # Relaciones
    vertical = relationship("Vertical", back_populates="attributes")
    attribute = relationship("Attribute", back_populates="verticals")