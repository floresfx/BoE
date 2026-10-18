"""Servicio de Cálculo de Costos de Bundle."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    Bundle,
    BundleComponent,
    Resource,
    Supplier,
    SupplierResource,
)
from app.schemas.bundle_cost import (
    BundleCostBreakdown,
    BundleCostLine,
    BundleCostResponse,
)


def calculate_bundle_cost(
    db: Session,
    bundle_id: UUID,
    multiplier: Decimal = Decimal("1.0"),
) -> BundleCostResponse:
    """Calcula el costo total de un bundle."""
    bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
    if not bundle:
        raise HTTPException(404, "Bundle no encontrado")

    components = (
        db.query(BundleComponent).filter(BundleComponent.bundle_id == bundle_id).all()
    )

    lines: list[BundleCostLine] = []
    total_materials = Decimal("0.0")
    total_waste = Decimal("0.0")

    for component in components:
        resource = db.query(Resource).filter(Resource.id == component.resource_id).first()
        if not resource:
            continue

        # Oferta más barata
        offer = (
            db.query(SupplierResource, Supplier)
            .join(Supplier, SupplierResource.supplier_id == Supplier.id)
            .filter(SupplierResource.resource_id == resource.id)
            .order_by(SupplierResource.unit_price.asc())
            .first()
        )

        if offer:
            supplier_offer, supplier = offer
            unit_cost = supplier_offer.unit_price
            supplier_used = supplier.name
        else:
            unit_cost = resource.cost or Decimal("0.0")
            supplier_used = None

        quantity = component.quantity
        waste_percent = resource.waste_percent or Decimal("0.0")

        line_cost = quantity * unit_cost
        waste_cost = line_cost * (waste_percent / Decimal("100"))
        total_line = line_cost + waste_cost

        total_materials += line_cost
        total_waste += waste_cost

        lines.append(
            BundleCostLine(
                resource_id=resource.id,
                resource_name=resource.name,
                quantity=quantity,
                unit_cost=unit_cost,
                line_cost=total_line,
                waste_percent=waste_percent,
                waste_cost=waste_cost,
                supplier_used=supplier_used,
            )
        )

    materials_cost = total_materials * multiplier
    waste_cost = total_waste * multiplier
    labor_cost = Decimal("0.0")  # TODO: fase 2
    overhead_cost = Decimal("0.0")  # TODO: fase 2
    total_cost = materials_cost + waste_cost + labor_cost + overhead_cost

    # Moneda base del tenant (fallback a USD)
    from app.models import Tenant
    from app.core.database import SessionLocal

    currency_code = "USD"

    return BundleCostResponse(
        bundle_id=bundle.id,
        bundle_name=bundle.name,
        multiplier=multiplier,
        total_cost=total_cost,
        currency_code=currency_code,
        breakdown=BundleCostBreakdown(
            materials_cost=materials_cost,
            waste_cost=waste_cost,
            labor_cost=labor_cost,
            overhead_cost=overhead_cost,
        ),
        lines=lines,
    )