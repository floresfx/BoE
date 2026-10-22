"""Servicio de bundles: explosión de paquetes (multinivel)."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Bundle, BundleComponent, Resource, Tenant, Unit


def _get_unit_symbol(db: Session, resource: Resource) -> str | None:
    """Obtiene el símbolo de la unidad base de un recurso."""
    if not resource.base_unit_id:
        return None
    unit = db.query(Unit).filter(Unit.id == resource.base_unit_id).first()
    return unit.symbol if unit else None


def _explode_recursive(
    db: Session,
    bundle: Bundle,
    multiplier: Decimal,
    season: str | None,
    depth: int,
    accumulated: dict[UUID, dict],
    max_depth: int = 5,
) -> None:
    """Explota un bundle recursivamente y acumula los recursos."""
    if depth > max_depth:
        raise HTTPException(
            400, f"Profundidad máxima de bundles excedida (>{max_depth})"
        )

    components = (
        db.query(BundleComponent)
        .filter(BundleComponent.bundle_id == bundle.id)
        .all()
    )

    for comp in components:
        # Filtrar por temporada (si se especifica)
        if season and comp.season and comp.season != season:
            continue

        # Calcular cantidad con merma
        qty = comp.quantity * multiplier
        if comp.waste_percent and comp.waste_percent > 0:
            qty = qty / (Decimal("1") - (comp.waste_percent / Decimal("100")))

        # Si es un sub-bundle, expandir recursivamente
        if comp.component_type == "bundle" and comp.component_bundle_id:
            sub_bundle = (
                db.query(Bundle)
                .filter(Bundle.id == comp.component_bundle_id)
                .first()
            )
            if not sub_bundle:
                raise HTTPException(
                    404, f"Sub-bundle no encontrado: {comp.component_bundle_id}"
                )
            _explode_recursive(
                db, sub_bundle, qty, season, depth + 1, accumulated, max_depth
            )
        # Si es un recurso, acumular
        elif comp.resource_id:
            resource = (
                db.query(Resource)
                .filter(Resource.id == comp.resource_id)
                .first()
            )
            if not resource:
                raise HTTPException(
                    404, f"Recurso no encontrado: {comp.resource_id}"
                )

            if comp.resource_id in accumulated:
                accumulated[comp.resource_id]["required_quantity"] += qty
            else:
                accumulated[comp.resource_id] = {
                    "resource_id": comp.resource_id,
                    "resource_name": resource.name,
                    "resource_unit_symbol": _get_unit_symbol(db, resource),
                    "required_quantity": qty,
                    "notes": comp.notes,
                }


def explode_bundle(
    db: Session,
    tenant: Tenant,
    bundle_id: UUID,
    multiplier: Decimal = Decimal("1"),
    season: str | None = None,
) -> dict:
    """Explota un bundle multinivel: devuelve la lista plana de recursos."""
    if multiplier <= 0:
        raise HTTPException(400, "El multiplicador debe ser > 0")

    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))

    bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
    if not bundle:
        db.execute(text('SET search_path TO public'))
        raise HTTPException(404, "Bundle no encontrado")

    accumulated: dict[UUID, dict] = {}
    _explode_recursive(db, bundle, multiplier, season, depth=0, accumulated=accumulated)

    db.execute(text('SET search_path TO public'))

    exploded = list(accumulated.values())

    return {
        "bundle_id": bundle.id,
        "bundle_code": bundle.code,
        "bundle_name": bundle.name,
        "multiplier": multiplier,
        "season": season,
        "total_components": len(exploded),
        "components": exploded,
    }