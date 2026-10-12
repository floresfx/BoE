from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ProfileBase(BaseModel):
    """Campos base del perfil."""
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class ProfileCreate(ProfileBase):
    """Schema para crear un perfil."""
    pass


class ProfileUpdate(BaseModel):
    """Schema para actualizar un perfil."""
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class ProfileResponse(ProfileBase):
    """Schema de respuesta del perfil."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}