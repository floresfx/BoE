"""Modelo ResourceTax — N:M entre Resource y Tax.

Vive en el schema del tenant.

Un recurso puede tener 0, 1 o N impuestos aplicables.
Ejemplo:
    harina → IVA 16%
    medicamento → IVA 16% + ISLR
"""

from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class ResourceTax(TenantBase, UUIDMixin, TimestampMixin):
    """Relación N:M entre Resource y Tax."""
    __tablename__ = "resources_taxes"
    __table_args__ = (
        UniqueConstraint(
            "resource_id", "tax_id",
            name="uq_resource_tax"
        ),
        Index("ix_resource_tax_resource_id", "resource_id"),
    )

    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    tax_id: Mapped[UUID] = mapped_column(
        ForeignKey("taxes.id"), nullable=False
    )

    # Relaciones
    resource = relationship("Resource", back_populates="taxes")