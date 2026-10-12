"""Schemas Pydantic para Resource."""

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


class ResourceBase(BaseModel):
    """Campos base del recurso."""
    name: str = Field(..., min_length=1, max_length=255)
    resource_type: ResourceType
    category: str | None = Field(default=None, max_length=100)
    base_unit: str = Field(..., min_length=1, max_length=20)
    cost: Decimal | None = Field(default=None, ge=0)
    is_active: bool = True


class ResourceCreate(ResourceBase):
    """Schema para crear un recurso."""
    pass


class ResourceUpdate(BaseModel):
    """Schema para actualizar un recurso."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    resource_type: ResourceType | None = None
    category: str | None = Field(default=None, max_length=100)
    base_unit: str | None = Field(default=None, min_length=1, max_length=20)
    cost: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ResourceResponse(ResourceBase):
    """Schema de respuesta del recurso."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ResourceListResponse(BaseSchema):
    """Lista paginada de recursos."""
    items: list[ResourceResponse]
    total: int