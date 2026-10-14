"""Schemas Pydantic para ResourceAttribute.

Fase 2: N:M entre Resource y Attribute con valor.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResourceAttributeCreate(BaseModel):
    """Schema para asignar un atributo a un recurso."""
    attribute_id: UUID
    value: str | None = None


class ResourceAttributeUpdate(BaseModel):
    """Schema para actualizar el valor de un atributo."""
    value: str | None = None


class ResourceAttributeResponse(BaseModel):
    """Schema de respuesta de un atributo de recurso."""
    id: UUID
    resource_id: UUID
    attribute_id: UUID
    value: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}