"""Schemas para la recepción de mercancía."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ReceiveLineIn(BaseModel):
    """Línea recibida: qué llegó y en qué condiciones."""

    line_id: UUID = Field(..., description="ID de la línea original")
    received_quantity: Decimal = Field(
        ...,
        gt=0,
        description="Cantidad efectivamente recibida",
    )
    lot_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código de lote (obligatorio)",
    )
    unit_cost: Decimal | None = Field(
        None,
        ge=0,
        description="Costo unitario (opcional, si no se toma del movimiento)",
    )
    expiration: datetime | None = Field(
        None,
        description="Fecha de caducidad (opcional)",
    )
    notes: str | None = Field(None, description="Notas de la recepción")


class ReceiveRequest(BaseModel):
    """Request para recibir mercancía de una solicitud."""

    warehouse_id: UUID = Field(
        ...,
        description="Warehouse destino",
    )
    lines: list[ReceiveLineIn] = Field(
        ...,
        min_length=1,
        description="Líneas recibidas",
    )
    notes: str | None = Field(
        None,
        description="Notas generales de la recepción",
    )


class ReceiveLineResponse(BaseSchema):
    """Respuesta de una línea recibida."""

    line_id: UUID
    resource_id: UUID
    resource_name: str
    quantity_received: Decimal
    lot_code: str
    movement_id: UUID


class ReceiveResponse(BaseSchema):
    """Respuesta de la recepción."""

    request_id: UUID
    request_code: str
    new_status: str
    lines: list[ReceiveLineResponse]
    message: str