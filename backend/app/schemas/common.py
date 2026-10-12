from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Schema base para todos los schemas."""
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Schema con timestamps."""
    created_at: datetime
    updated_at: datetime


class UUIDResponse(BaseSchema):
    """Respuesta con solo UUID."""
    id: UUID


class MessageResponse(BaseSchema):
    """Respuesta con mensaje."""
    message: str


class ErrorResponse(BaseSchema):
    """Respuesta de error."""
    detail: str