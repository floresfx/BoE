"""Modelo Resource — recurso operativo por tenant.

Vive en el schema del tenant (search_path dinámico).
NO tiene `tenant_id`: el schema ya aísla.

Relaciones:
- category_id    → categories (global)
- subcategory_id → subcategories (global)
- base_unit_id   → units (global)
- attributes     → N:M vía resources_attributes
- taxes          → N:M vía resources_taxes
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase

# Los 8 tipos de recurso (ver DOCUMENTO 1 MPR, sección 12.2)
RESOURCE_TYPES = (
    "materia_prima",
    "producto_terminado",
    "subproducto",
    "insumo",
    "servicio_propio",
    "servicio_externo",
    "recurso_humano",
    "recurso_fisico",
)


class Resource(TenantBase, UUIDMixin, TimestampMixin):
    """Recurso operativo: materiales, servicios, recursos humanos, etc.

    Vive en el schema del tenant. Se accede vía search_path.
    """
    __tablename__ = "resources"
    __table_args__ = (
        Index("ix_resource_name", "name"),
        Index("ix_resource_type", "resource_type"),
        Index("ix_resource_is_active", "is_active"),
        Index("ix_resource_category_id", "category_id"),
        Index("ix_resource_subcategory_id", "subcategory_id"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)

    # FKs a datos maestros globales
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    subcategory_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("subcategories.id"), nullable=True
    )
    base_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("units.id"), nullable=False
    )

    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    waste_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0, server_default="0"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Relaciones
    attributes = relationship(
        "ResourceAttribute",
        back_populates="resource",
        cascade="all, delete-orphan",
    )
    taxes = relationship(
        "ResourceTax",
        back_populates="resource",
        cascade="all, delete-orphan",
    )