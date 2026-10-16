"""Modelo SupplierResource — N:M entre Supplier y Resource."""

from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class SupplierResource(TenantBase, UUIDMixin, TimestampMixin):
    """Un proveedor puede suministrar varios recursos."""

    __tablename__ = "supplier_resources"
    __table_args__ = (
        UniqueConstraint(
            "supplier_id", "resource_id",
            name="uq_supplier_resource",
        ),
        Index("ix_supplier_resource_supplier", "supplier_id"),
        Index("ix_supplier_resource_resource", "resource_id"),
    )

    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    supplier = relationship("Supplier", back_populates="resources")