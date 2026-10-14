"""Schemas para suscripción y selección de plan."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class PlanSummary(BaseSchema):
    """Resumen de un plan para el frontend."""
    id: UUID
    code: str
    name: str
    price: Decimal
    currency_code: str
    interval: str
    trial_days: int
    features: list[str]
    limits: dict[str, int | None]


class SubscriptionInfo(BaseSchema):
    """Estado de la suscripción del tenant."""
    plan_id: UUID | None
    plan_name: str | None
    status: str  # "trial", "activo", "pausado", "sin_plan"
    trial_ends_at: datetime | None
    days_remaining: int | None


class SelectPlanRequest(BaseModel):
    """Body para seleccionar un plan."""
    plan_id: UUID


class SelectPlanResponse(BaseSchema):
    """Respuesta al seleccionar un plan."""
    plan_id: UUID
    plan_name: str
    status: str
    trial_ends_at: datetime | None
    message: str