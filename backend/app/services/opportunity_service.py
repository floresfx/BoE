"""Servicio del Motor de Oportunidades (Matching Inverso)."""

import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Bundle, Tenant
from app.schemas.opportunity import (
    OpportunityBottleneck,
    OpportunityResponse,
)
from app.services.availability_service import check_availability
from app.services.bundle_cost_service import calculate_bundle_cost
from app.services.bundle_service import explode_bundle

logger = logging.getLogger(__name__)


def find_opportunities(
    db: Session,
    tenant: Tenant,
    min_coverage: Decimal = Decimal("50.0"),
) -> list[OpportunityResponse]:
    """Encuentra oportunidades: qué bundles se pueden producir con el stock actual.

    Args:
        db: sesión SQLAlchemy.
        tenant: tenant actual.
        min_coverage: cobertura mínima para incluir una oportunidad (0-100).

    Returns:
        Lista de oportunidades ordenadas por margen estimado descendente.
    """
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))

    bundles = db.query(Bundle).filter(Bundle.is_active == True).all()
    opportunities = []

    for bundle in bundles:
        # 1. Explotar el bundle (multiplier=1)
        try:
            exploded = explode_bundle(db, tenant, bundle.id, Decimal("1"))
            logger.info(f"Bundle {bundle.code}: exploded = {exploded}")
        except Exception as e:
            logger.error(f"Bundle {bundle.code}: explode_bundle failed: {e}")
            continue

        components = exploded["components"]
        if not components:
            logger.warning(f"Bundle {bundle.code}: no components")
            continue

        # 2. Calcular costo del bundle
        try:
            cost_data = calculate_bundle_cost(db, tenant, bundle.id, Decimal("1"))
            estimated_cost = cost_data.total_cost
            logger.info(f"Bundle {bundle.code}: estimated_cost = {estimated_cost}")
        except Exception as e:
            logger.error(f"Bundle {bundle.code}: calculate_bundle_cost failed: {e}")
            estimated_cost = Decimal("0")

        # 3. Calcular margen
        estimated_margin = None
        estimated_margin_percent = None
        if bundle.sale_price and estimated_cost > 0:
            estimated_margin = bundle.sale_price - estimated_cost
            estimated_margin_percent = (estimated_margin / bundle.sale_price) * Decimal("100")

        # 4. Verificar disponibilidad de cada componente
        components_covered = 0
        max_producible = None
        worst_bottleneck = None

        for comp in components:
            availability = check_availability(
                db, tenant, comp["resource_id"], comp["required_quantity"]
            )

            # Calcular cuántos bundles se pueden producir con este componente
            if comp["required_quantity"] > 0 and availability.available_quantity > 0:
                producible = availability.available_quantity / comp["required_quantity"]
                if max_producible is None or producible < max_producible:
                    max_producible = producible
                    if availability.status.value != "covered":
                        worst_bottleneck = OpportunityBottleneck(
                            resource_id=comp["resource_id"],
                            resource_name=comp["resource_name"],
                            required_quantity=comp["required_quantity"],
                            available_quantity=availability.available_quantity,
                            missing_quantity=availability.missing_quantity,
                        )

            if availability.status.value == "covered":
                components_covered += 1
            elif availability.status.value == "out_of_stock":
                max_producible = Decimal("0")
                worst_bottleneck = OpportunityBottleneck(
                    resource_id=comp["resource_id"],
                    resource_name=comp["resource_name"],
                    required_quantity=comp["required_quantity"],
                    available_quantity=Decimal("0"),
                    missing_quantity=comp["required_quantity"],
                )
                break

        coverage_percent = (
            Decimal(components_covered) / Decimal(len(components)) * Decimal("100")
        )

        if coverage_percent < min_coverage:
            continue

        opportunities.append(
            OpportunityResponse(
                bundle_id=bundle.id,
                bundle_code=bundle.code,
                bundle_name=bundle.name,
                sale_price=bundle.sale_price,
                estimated_cost=estimated_cost,
                estimated_margin=estimated_margin,
                estimated_margin_percent=estimated_margin_percent,
                coverage_percent=coverage_percent,
                max_producible=max_producible or Decimal("0"),
                bottleneck=worst_bottleneck,
                components_covered=components_covered,
                components_total=len(components),
            )
        )

    db.execute(text('SET search_path TO public'))

    # Ordenar por margen descendente (None al final)
    opportunities.sort(
        key=lambda x: (x.estimated_margin or Decimal("-999999")), reverse=True
    )
    return opportunities