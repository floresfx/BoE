"""Modelo ResourceAttribute — N:M entre Resource y Attribute con valor.

Vive en el schema del tenant.

Ejemplo:
    resource=certificado por "Esterilizado" → value=None (booleano)
    resource=temperature por "Temperatura" → value="25"
    resource=origin por "Origen" → value="Importado"
"""

from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class ResourceAttribute(TenantBase, UUIDMixin, TimestampMixin):
    """Relación N:M entre Resource y Attribute con valor."""
    __tablename__ = "resources_attributes"
    __table_args__ = (
        UniqueConstraint(
            "resource_id", "attribute_id",
            name="uq_resource_attribute"
        ),
        Index("ix_resource_attr_resource_id", "resource_id"),
    )

    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    attribute_id: Mapped[UUID] = mapped_column(
        ForeignKey("attributes.id"), nullable=False
    )
    value: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    resource = relationship("Resource", back_populates="attributes")