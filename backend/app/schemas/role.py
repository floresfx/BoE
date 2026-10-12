from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class RoleBase(BaseModel):
    """Campos base del rol."""
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    is_system: bool = True


class RoleCreate(RoleBase):
    """Schema para crear un rol."""
    permission_ids: list[UUID] = []


class RoleUpdate(BaseModel):
    """Schema para actualizar un rol."""
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    permission_ids: list[UUID] | None = None


class RoleResponse(RoleBase):
    """Schema de respuesta del rol."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}