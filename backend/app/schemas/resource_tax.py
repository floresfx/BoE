"""Schemas Pydantic para ResourceTax.

Fase 2: N:M entre Resource y Tax.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ResourceTaxCreate(BaseModel):
    """Schema para asignar un impuesto a un recurso."""
    tax_id: UUID


class ResourceTaxResponse(BaseModel):
    """Schema de respuesta de un impuesto de recurso."""
    id: UUID
    resource_id: UUID
    tax_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}