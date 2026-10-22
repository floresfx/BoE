# app/services/availability_service.py
from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import (
    Bundle,
    Currency,
    Resource,
    StockLot,
    StockReservation,
    Supplier,
    SupplierResource,
    Tenant,
    Warehouse,
)
from app.schemas.availability import (
    AvailabilityResponse,
    AvailabilityStatus,
    BundleAvailabilityResponse,
    SupplierSuggestion,
    WarehouseAvailability,
)
from app.services.bundle_service import explode_bundle


def _set_tenant_schema(db: Session, tenant: Tenant) -> None:
    """Aplica el search_path del tenant en la sesión actual."""
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))


def _reset_search_path(db: Session) -> None:
    """Resetea el search_path a public."""
    db.execute(text('SET search_path TO public'))


def _get_available_stock(
    db: Session,
    resource_id: UUID,
    warehouse_id: UUID | None = None,
) -> Decimal:
    """Calcula el stock disponible (lotes no vencidos - reservas activas)."""
    now = datetime.now(timezone.utc)

    stock_query = db.query(func.sum(StockLot.quantity)).filter(
        StockLot.resource_id == resource_id,
        or_(StockLot.expiration.is_(None), StockLot.expiration > now),
    )
    if warehouse_id:
        stock_query = stock_query.filter(StockLot.warehouse_id == warehouse_id)
    total_stock = stock_query.scalar() or Decimal("0.0")

    reservation_query = db.query(func.sum(StockReservation.quantity)).filter(
        StockReservation.resource_id == resource_id,
        StockReservation.status.in_(["pending", "confirmed"]),
    )
    if warehouse_id:
        reservation_query = reservation_query.filter(
            StockReservation.warehouse_id == warehouse_id
        )
    total_reserved = reservation_query.scalar() or Decimal("0.0")

    return total_stock - total_reserved


def _get_warehouse_breakdown(
    db: Session, resource_id: UUID
) -> list[WarehouseAvailability]:
    """Desglose de stock por almacén (lotes no vencidos - reservas)."""
    warehouses = db.query(Warehouse).all()
    breakdown = []
    for wh in warehouses:
        available = _get_available_stock(db, resource_id, wh.id)
        if available > 0:
            breakdown.append(
                WarehouseAvailability(
                    warehouse_id=wh.id,
                    warehouse_name=wh.name,
                    available=available,
                )
            )
    return breakdown


def _get_supplier_suggestions(
    db: Session, resource_id: UUID, missing_quantity: Decimal
) -> list[SupplierSuggestion]:
    """Busca ofertas de proveedores para cubrir el faltante."""
    offers = (
        db.query(SupplierResource, Supplier)
        .join(Supplier, SupplierResource.supplier_id == Supplier.id)
        .filter(SupplierResource.resource_id == resource_id)
        .filter(SupplierResource.unit_price.isnot(None))
        .order_by(SupplierResource.unit_price.asc())
        .limit(5)
        .all()
    )
    suggestions = []
    for offer, supplier in offers:
        currency = (
            db.query(Currency).filter(Currency.id == offer.currency_id).first()
            if offer.currency_id
            else None
        )
        suggestions.append(
            SupplierSuggestion(
                supplier_id=supplier.id,
                supplier_name=supplier.name,
                unit_price=offer.unit_price or Decimal("0"),
                lead_time_days=offer.lead_time_days or 0,
                currency_code=currency.code if currency else "USD",
            )
        )
    return suggestions


def check_availability(
    db: Session,
    tenant: Tenant,
    resource_id: UUID,
    required_quantity: Decimal,
) -> AvailabilityResponse:
    """Calcula la disponibilidad de un solo recurso (con reservas y caducidad)."""
    _set_tenant_schema(db, tenant)

    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise ValueError(f"Recurso con id {resource_id} no encontrado.")

    available_quantity = _get_available_stock(db, resource_id)
    missing_quantity = max(Decimal("0.0"), required_quantity - available_quantity)

    if missing_quantity == 0:
        status = AvailabilityStatus.COVERED
    elif available_quantity == 0:
        status = AvailabilityStatus.OUT_OF_STOCK
    else:
        status = AvailabilityStatus.PARTIAL

    suppliers = []
    if missing_quantity > 0:
        suppliers = _get_supplier_suggestions(db, resource_id, missing_quantity)

    warehouses = _get_warehouse_breakdown(db, resource_id)

    _reset_search_path(db)

    return AvailabilityResponse(
        resource_id=resource.id,
        resource_name=resource.name,
        required_quantity=required_quantity,
        available_quantity=available_quantity,
        missing_quantity=missing_quantity,
        status=status,
        suppliers=suppliers,
        warehouses=warehouses,
    )


def check_bundle_availability(
    db: Session,
    tenant: Tenant,
    bundle_id: UUID,
    multiplier: Decimal,
    season: str | None = None,
) -> BundleAvailabilityResponse:
    """Calcula la disponibilidad de un bundle multinivel explotado."""
    _set_tenant_schema(db, tenant)

    bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
    if not bundle:
        raise ValueError(f"Bundle con id {bundle_id} no encontrado.")

    exploded = explode_bundle(db, tenant, bundle_id, multiplier, season)
    lines = []
    overall_status = AvailabilityStatus.COVERED

    for comp in exploded["components"]:
        availability = check_availability(
            db, tenant, comp["resource_id"], comp["required_quantity"]
        )
        lines.append(availability)

        if availability.status == AvailabilityStatus.OUT_OF_STOCK:
            overall_status = AvailabilityStatus.OUT_OF_STOCK
        elif (
            availability.status == AvailabilityStatus.PARTIAL
            and overall_status != AvailabilityStatus.OUT_OF_STOCK
        ):
            overall_status = AvailabilityStatus.PARTIAL

    _reset_search_path(db)

    return BundleAvailabilityResponse(
        bundle_id=bundle.id,
        bundle_name=bundle.name,
        multiplier=multiplier,
        overall_status=overall_status,
        lines=lines,
    )