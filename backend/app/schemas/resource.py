"""Schemas Pydantic para Resource.

Fase 2: refactor con FKs a datos maestros globales.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

# Los 8 tipos válidos (coinciden con RESOURCE_TYPES del modelo)
ResourceType = Literal[
    "materia_prima",
    "producto_terminado",
    "subproducto",
    "insumo",
    "servicio_propio",
    "servicio_externo",
    "recurso_humano",
    "recurso_fisico",
]


# ---------------------------------------------------------------------------
# Atributos inline (para crear/actualizar recursos con sus atributos)
# ---------------------------------------------------------------------------

class ResourceAttributeInline(BaseModel):
    """Atributo inline para crear/actualizar un recurso."""
    attribute_id: UUID
    value: str | None = None


class ResourceTaxInline(BaseModel):
    """Impuesto inline para crear/actualizar un recurso."""
    tax_id: UUID


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------

class ResourceBase(BaseModel):
    """Campos base del recurso."""
    name: str = Field(..., min_length=1, max_length=255)
    resource_type: ResourceType
    category_id: UUID | None = None
    subcategory_id: UUID | None = None
    base_unit_id: UUID  # ← obligatorio
    cost: Decimal | None = Field(default=None, ge=0)
    is_active: bool = True


class ResourceCreate(ResourceBase):
    """Schema para crear un recurso.

    Permite crear atributos e impuestos inline (transaccional).
    """
    attributes: list[ResourceAttributeInline] = Field(default_factory=list)
    taxes: list[ResourceTaxInline] = Field(default_factory=list)


class ResourceUpdate(BaseModel):
    """Schema para actualizar un recurso.

    Los atributos e impuestos se gestionan con endpoints dedicados.
    """
    name: str | None = Field(default=None, min_length=1, max_length=255)
    resource_type: ResourceType | None = None
    category_id: UUID | None = None
    subcategory_id: UUID | None = None
    base_unit_id: UUID | None = None
    cost: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response: incluye atributos e impuestos anidados
# ---------------------------------------------------------------------------

class ResourceAttributeResponse(BaseModel):
    """Atributo de un recurso en la respuesta."""
    attribute_id: UUID
    attribute_code: str  # ← viene del join con attributes
    attribute_name: str  # ← viene del join con attributes
    value: str | None

    model_config = {"from_attributes": True}


class ResourceTaxResponse(BaseModel):
    """Impuesto de un recurso en la respuesta."""
    tax_id: UUID
    tax_code: str  # ← viene del join con taxes
    tax_name: str  # ← viene del join con taxes
    tax_rate: Decimal  # ← viene del join con taxes

    model_config = {"from_attributes": True}


class ResourceResponse(ResourceBase):
    """Schema de respuesta del recurso."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Relaciones (pueden venir vacías)
    attributes: list[ResourceAttributeResponse] = Field(default_factory=list)
    taxes: list[ResourceTaxResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ResourceListResponse(BaseSchema):
    """Lista paginada de recursos."""
    items: list[ResourceResponse]
    total: int