# app/schemas/availability.py
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema # Asumo que tienes este import, si no, usa BaseModel


class AvailabilityStatus(str, Enum):
    """Estados posibles de disponibilidad."""
    COVERED = "covered"
    PARTIAL = "partial"
    OUT_OF_STOCK = "out_of_stock"


class WarehouseAvailability(BaseSchema):
    """Desglose de stock por almacén."""
    warehouse_id: UUID
    warehouse_name: str
    available: Decimal


class SupplierSuggestion(BaseSchema):
    """Sugerencia de un proveedor para cubrir el faltante."""
    supplier_id: UUID
    supplier_name: str
    unit_price: Decimal
    lead_time_days: int
    currency_code: str


class AvailabilityResponse(BaseSchema):
    """Respuesta del cálculo de disponibilidad para un recurso."""
    resource_id: UUID
    resource_name: str
    required_quantity: Decimal
    available_quantity: Decimal
    missing_quantity: Decimal
    status: AvailabilityStatus
    warehouses: list[WarehouseAvailability] = []
    suppliers: list[SupplierSuggestion] = []


class AvailabilityRequest(BaseModel):
    """Request para verificar un recurso suelto."""
    resource_id: UUID
    quantity: Decimal = Field(..., gt=0, description="Cantidad requerida para la verificación.")


# --- Schemas para Bundles ---

class BundleAvailabilityRequest(BaseModel):
    """Request para verificar la disponibilidad de un bundle."""
    bundle_id: UUID
    multiplier: Decimal = Field(1.0, gt=0, description="Multiplicador del bundle a verificar.")


class BundleAvailabilityResponse(BaseSchema):
    """Respuesta del cálculo de disponibilidad para un bundle."""
    bundle_id: UUID
    bundle_name: str
    multiplier: Decimal
    overall_status: AvailabilityStatus
    lines: list[AvailabilityResponse]