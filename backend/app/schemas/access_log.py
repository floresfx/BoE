from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class AccessLogBase(BaseModel):
    """Campos base del log."""
    event: str = Field(..., min_length=1, max_length=50)
    ip: str | None = Field(default=None, max_length=50)
    user_agent: str | None = Field(default=None, max_length=500)


class AccessLogCreate(AccessLogBase):
    """Schema para crear un log."""
    user_id: UUID
    tenant_id: UUID


class AccessLogResponse(AccessLogBase):
    """Schema de respuesta del log."""
    id: UUID
    user_id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}