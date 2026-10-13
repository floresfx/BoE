from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class PlanBase(BaseModel):
    """Campos base del plan."""
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=50)
    price: Decimal = Field(..., ge=0)
    currency_id: UUID
    interval: str = Field(..., min_length=1, max_length=20)
    trial_days: int = Field(default=0, ge=0)
    is_active: bool = True


class PlanCreate(PlanBase):
    """Schema para crear un plan."""
    pass


class PlanUpdate(BaseModel):
    """Schema para actualizar un plan.

    `code` no es editable (identifica al plan).
    """
    name: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, ge=0)
    currency_id: UUID | None = None
    interval: str | None = Field(default=None, min_length=1, max_length=20)
    trial_days: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class PlanResponse(PlanBase):
    """Schema de respuesta del plan."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}