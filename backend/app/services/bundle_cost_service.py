"""Servicio de costos de bundle."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    Bundle,
    BundleComponent,
    Currency,
    Resource,
    Supplier,
    SupplierResource,
    Tenant,
)
from app.schemas.bundle_cost import (
    BundleCostBreakdown,
    BundleCostLine,
    BundleCostResponse,
)


def _set_tenant_schema(db: Session, tenant: Tenant) -> None:
    """Aplica el search_path del tenant."""
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))


def _reset_search_path(db: Session) -> None:
    """Resetea el search_path a public."""
    db.execute(text('SET search_path TO public'))


def _get_currency_code(db: Session, tenant: Tenant) -> str:
    """Obtiene el código de la moneda base del tenant."""
    if tenant.base_currency_id:
        currency = (
            db.query(Currency)
            .filter(Currency.id == tenant.base_currency_id)
            .first()
        )
        if currency:
            return currency.code
    return "USD"


def calculate_bundle_cost(
    db: Session,
    tenant: Tenant,
    bundle_id: UUID,
    multiplier: Decimal = Decimal("1"),
) -> BundleCostResponse:
    """Calcula el costo total de un bundle.

    Args:
        db: sesión SQLAlchemy.
        tenant: tenant actual.
        bundle_id: ID del bundle.
        multiplier: multiplicador (cantidad de bundles).

    Returns:
        BundleCostResponse con el desglose de costos.

    Raises:
        404 si el bundle no existe.
    """
    if multiplier <= 0:
        raise HTTPException(400, "El multiplicador debe ser > 0")

    _set_tenant_schema(db, tenant)

    bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
    if not bundle:
        _reset_search_path(db)
        raise HTTPException(404, "Bundle no encontrado")

    currency_code = _get_currency_code(db, tenant)

    components = (
        db.query(BundleComponent)
        .filter(BundleComponent.bundle_id == bundle_id)
        .all()
    )

    lines = []
    total_cost = Decimal("0")
    total_waste_cost = Decimal("0")
    total_materials_cost = Decimal("0")

    for comp in components:
        if comp.component_type != "resource" or not comp.resource_id:
            continue

        resource = (
            db.query(Resource)
            .filter(Resource.id == comp.resource_id)
            .first()
        )
        if not resource:
            continue

        # Buscar la oferta más barata del proveedor
        offer = (
            db.query(SupplierResource, Supplier)
            .join(Supplier, SupplierResource.supplier_id == Supplier.id)
            .filter(SupplierResource.resource_id == comp.resource_id)
            .filter(SupplierResource.unit_price.isnot(None))
            .order_by(SupplierResource.unit_price.asc())
            .first()
        )

        if offer:
            supplier_resource, supplier = offer
            unit_cost = supplier_resource.unit_price
            supplier_used = supplier.name
        else:
            unit_cost = resource.cost or Decimal("0")
            supplier_used = None

        # Cantidad base sin merma
        base_qty = comp.quantity * multiplier

        # Cantidad con merma (la merma se suma a la cantidad requerida)
        waste_pct = comp.waste_percent or Decimal("0")
        if waste_pct > 0:
            qty_with_waste = base_qty / (Decimal("1") - (waste_pct / Decimal("100")))
        else:
            qty_with_waste = base_qty

        # Costo de la línea (con merma incluida)
        line_cost = qty_with_waste * unit_cost

        # Costo de la merma (diferencia entre con merma y sin merma)
        waste_cost = (qty_with_waste - base_qty) * unit_cost

        total_cost += line_cost
        total_waste_cost += waste_cost
        total_materials_cost += base_qty * unit_cost

        lines.append(
            BundleCostLine(
                resource_id=comp.resource_id,
                resource_name=resource.name,
                quantity=qty_with_waste,
                unit_cost=unit_cost,
                line_cost=line_cost,
                waste_percent=waste_pct,
                waste_cost=waste_cost,
                supplier_used=supplier_used,
            )
        )

    _reset_search_path(db)

    breakdown = BundleCostBreakdown(
        materials_cost=total_materials_cost,
        waste_cost=total_waste_cost,
        labor_cost=Decimal("0"),
        overhead_cost=Decimal("0"),
    )

    return BundleCostResponse(
        bundle_id=bundle.id,
        bundle_name=bundle.name,
        multiplier=multiplier,
        total_cost=total_cost,
        currency_code=currency_code,
        breakdown=breakdown,
        lines=lines,
    )