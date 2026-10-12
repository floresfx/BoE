from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class PermissionBase(BaseModel):
    """Campos base del permiso."""
    module: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class PermissionCreate(PermissionBase):
    """Schema para crear un permiso."""
    pass


class PermissionUpdate(BaseModel):
    """Schema para actualizar un permiso."""
    module: str | None = Field(default=None, min_length=1, max_length=50)
    action: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class PermissionResponse(PermissionBase):
    """Schema de respuesta del permiso."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}