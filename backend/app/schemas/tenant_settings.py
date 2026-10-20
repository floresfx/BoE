"""Schemas para la configuración de la fundación del tenant."""

from uuid import UUID

from pydantic import BaseModel


class TenantSettingsUpdate(BaseModel):
    """Schema para actualizar la configuración de la fundación de un tenant."""

    base_currency_id: UUID | None = None
    inventory_costing_method: str | None = None
    active_unit_ids: list[UUID] | None = None
    active_category_ids: list[UUID] | None = None
    active_attribute_ids: list[UUID] | None = None


class TenantSettingsResponse(BaseModel):
    """Schema de respuesta con la configuración actual del tenant."""

    base_currency_id: UUID | None
    inventory_costing_method: str
    active_unit_ids: list[UUID]
    active_category_ids: list[UUID]
    active_attribute_ids: list[UUID]

    model_config = {"from_attributes": True}