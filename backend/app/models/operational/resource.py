"""Modelo Resource — recurso operativo por tenant.

Vive en el schema del tenant (search_path dinámico).
NO tiene `tenant_id`: el schema ya aísla.
"""

from decimal import Decimal

from sqlalchemy import Boolean, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_tenant import TenantBase
from app.models.base import TimestampMixin, UUIDMixin

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
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    base_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )