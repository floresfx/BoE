from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class PlanBase(BaseModel):
    """Campos base del plan."""
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=10)
    features: dict | None = None
    limits: dict | None = None
    is_active: bool = True


class PlanCreate(PlanBase):
    """Schema para crear un plan."""
    pass


class PlanUpdate(BaseModel):
    """Schema para actualizar un plan."""
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    features: dict | None = None
    limits: dict | None = None
    is_active: bool | None = None


class PlanResponse(PlanBase):
    """Schema de respuesta del plan."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}