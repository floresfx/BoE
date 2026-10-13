from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class VerticalBase(BaseModel):
    """Campos base del vertical."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class VerticalCreate(VerticalBase):
    """Schema para crear un vertical."""
    pass


class VerticalUpdate(BaseModel):
    """Schema para actualizar un vertical.

    `code` no es editable (identifica al vertical).
    """
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class VerticalResponse(VerticalBase):
    """Schema de respuesta del vertical."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}