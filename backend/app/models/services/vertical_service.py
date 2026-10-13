from uuid import UUID

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class VerticalService(Base, UUIDMixin, TimestampMixin):
    """Relacion N:M entre verticales y servicios."""
    __tablename__ = "verticals_services"
    __table_args__ = (
        UniqueConstraint(
            "vertical_id", "service_id", name="uq_vertical_service"
        ),
    )

    vertical_id: Mapped[UUID] = mapped_column(
        ForeignKey("verticals.id"), nullable=False, index=True
    )
    service_id: Mapped[UUID] = mapped_column(
        ForeignKey("service_templates.id"), nullable=False, index=True
    )
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    service = relationship("ServiceTemplate", back_populates="verticals")