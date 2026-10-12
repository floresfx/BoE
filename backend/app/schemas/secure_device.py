from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class SecureDeviceBase(BaseModel):
    """Campos base del dispositivo."""
    fingerprint: str = Field(..., min_length=1, max_length=255)
    ip: str | None = Field(default=None, max_length=50)


class SecureDeviceCreate(SecureDeviceBase):
    """Schema para crear un dispositivo."""
    pass


class SecureDeviceResponse(SecureDeviceBase):
    """Schema de respuesta del dispositivo."""
    id: UUID
    user_id: UUID
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}