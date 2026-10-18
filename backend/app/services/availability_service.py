# app/services/availability_service.py
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import text


from app.models import (
    Bundle,
    BundleComponent,
    Resource,
    StockLot,
    Supplier,
    SupplierResource,
)
from app.schemas.availability import (
    AvailabilityResponse,
    AvailabilityStatus,
    BundleAvailabilityResponse,
    SupplierSuggestion,
    WarehouseAvailability,
)


def check_availability(
    db: Session,
    resource_id: UUID,
    required_quantity: Decimal,
) -> AvailabilityResponse:
    """
    Calcula la disponibilidad de un solo recurso.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise ValueError(f"Recurso con id {resource_id} no encontrado.")

    # 1. Calcular stock disponible consolidado
    available_quantity = (
        db.query(func.sum(StockLot.quantity))
        .filter(StockLot.resource_id == resource_id)
        .scalar()
    ) or Decimal("0.0")

    # 2. Calcular faltante
    missing_quantity = max(Decimal("0.0"), required_quantity - available_quantity)

    # 3. Determinar estado
    if missing_quantity == 0:
        status = AvailabilityStatus.COVERED
    elif available_quantity == 0:
        status = AvailabilityStatus.OUT_OF_STOCK
    else:
        status = AvailabilityStatus.PARTIAL

    # 4. Buscar proveedores sugeridos si hay faltante
        # 4. Buscar proveedores sugeridos si hay faltante
        # 4. Buscar proveedores sugeridos si hay faltante
    suppliers = []
    if missing_quantity > 0:
        from app.models import Currency

        offers = (
            db.query(SupplierResource, Supplier)
            .join(Supplier, SupplierResource.supplier_id == Supplier.id)
            .filter(SupplierResource.resource_id == resource_id)
            .order_by(SupplierResource.unit_price.asc())
            .limit(5)
            .all()
        )
        for offer, supplier in offers:
            currency = (
                db.query(Currency).filter(Currency.id == offer.currency_id).first()
                if offer.currency_id
                else None
            )
            suppliers.append(
                SupplierSuggestion(
                    supplier_id=supplier.id,
                    supplier_name=supplier.name,
                    unit_price=offer.unit_price or Decimal("0"),
                    lead_time_days=offer.lead_time_days or 0,
                    currency_code=currency.code if currency else "USD",
                )
            )

    return AvailabilityResponse(
        resource_id=resource.id,
        resource_name=resource.name,
        required_quantity=required_quantity,
        available_quantity=available_quantity,
        missing_quantity=missing_quantity,
        status=status,
        suppliers=suppliers,
        # TODO: Implementar el desglose por warehouse si es necesario
        warehouses=[],
    )


def check_bundle_availability(
    db: Session,
    bundle_id: UUID,
    multiplier: Decimal,
) -> BundleAvailabilityResponse:
    """
    Calcula la disponibilidad de un bundle completo explotando sus componentes.
    """
    bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
    if not bundle:
        raise ValueError(f"Bundle con id {bundle_id} no encontrado.")

    components = (
        db.query(BundleComponent)
        .filter(BundleComponent.bundle_id == bundle_id)
        .all()
    )

    lines = []
    overall_status = AvailabilityStatus.COVERED

    for component in components:
        required_quantity = component.quantity * multiplier
        availability = check_availability(db, component.resource_id, required_quantity)
        lines.append(availability)

        # El estado general es el peor de todos los componentes
        if availability.status == AvailabilityStatus.OUT_OF_STOCK:
            overall_status = AvailabilityStatus.OUT_OF_STOCK
        elif availability.status == AvailabilityStatus.PARTIAL and overall_status != AvailabilityStatus.OUT_OF_STOCK:
            overall_status = AvailabilityStatus.PARTIAL

    return BundleAvailabilityResponse(
        bundle_id=bundle.id,
        bundle_name=bundle.name,
        multiplier=multiplier,
        overall_status=overall_status,
        lines=lines,
    )