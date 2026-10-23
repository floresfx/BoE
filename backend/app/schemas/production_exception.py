"""Schemas para excepciones operativas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ProductionOrderExceptionRequest(BaseModel):
    """Request para marcar una excepción en una orden de producción."""
    exception_type: str = Field(
        ...,
        description="not_executed | partial | with_deviation",
    )
    notes: str | None = None
    actual_quantity: Decimal | None = Field(
        None,
        description="Cantidad real producida (solo para 'partial' o 'with_deviation')",
    )


class ProductionOrderExceptionResponse(BaseSchema):
    """Response de la excepción aplicada."""
    order_id: UUID
    order_code: str
    exception_type: str
    message: str
    restored_quantity: Decimal = Decimal("0")