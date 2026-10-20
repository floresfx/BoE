from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema

TenantStatus = Literal["activo", "suspendido", "cancelado"]


class TenantBase(BaseModel):
    """Campos base del tenant."""
    name: str = Field(..., min_length=1, max_length=255)
    tax_id: str = Field(..., min_length=1, max_length=50)
    tax_id_type: str = Field(..., min_length=1, max_length=20)
    admin_email: EmailStr
    timezone: str = Field(default="America/Caracas", max_length=50)
    country: str = Field(..., min_length=1, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)


class TenantCreate(TenantBase):
    """Schema para crear un tenant."""
    vertical_id: UUID | None = None
    plan_id: UUID | None = None


class TenantUpdate(BaseModel):
    """Schema para actualizar un tenant."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    tax_id: str | None = Field(default=None, min_length=1, max_length=50)
    tax_id_type: str | None = Field(default=None, min_length=1, max_length=20)
    admin_email: EmailStr | None = None
    timezone: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    vertical_id: UUID | None = None
    plan_id: UUID | None = None
    status: TenantStatus | None = None


class TenantResponse(TenantBase):
    """Schema de respuesta del tenant.

    No expone schema_name (interno del sistema).
    """
    id: UUID
    vertical_id: UUID | None
    plan_id: UUID | None
    status: TenantStatus
    inventory_costing_method: str = "fifo"
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class TenantListResponse(BaseSchema):
    """Lista de tenants."""
    items: list[TenantResponse]
    total: int

class TenantSettingsUpdate(BaseModel):
    inventory_costing_method: str | None = None