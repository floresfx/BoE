"""Servicio de bundles: explosión de paquetes."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Bundle, BundleComponent, Resource


def explode_bundle(
    db: Session,
    bundle_id: UUID,
    multiplier: Decimal = Decimal("1"),
) -> dict:
    """Explota un bundle: devuelve la lista de recursos requeridos.

    Args:
        db: sesión SQLAlchemy.
        bundle_id: ID del bundle a explotar.
        multiplier: cuántas veces se multiplica el bundle
                    (ej: si el bundle es "lote 100 unidades" y quieres
                    500 unidades, multiplier = 5).

    Returns:
        dict con los datos del bundle y sus componentes multiplicados.

    Raises:
        404 si el bundle no existe.
        400 si el multiplier es <= 0.
    """
    if multiplier <= 0:
        raise HTTPException(400, "El multiplicador debe ser > 0")

    bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
    if not bundle:
        raise HTTPException(404, "Bundle no encontrado")

    components = (
        db.query(BundleComponent)
        .filter(BundleComponent.bundle_id == bundle_id)
        .all()
    )

    exploded = []
    for comp in components:
        resource = (
            db.query(Resource).filter(Resource.id == comp.resource_id).first()
        )
        if not resource:
            continue
        exploded.append({
            "resource_id": comp.resource_id,
            "resource_name": resource.name,
            "resource_unit_symbol": None,  # TODO: join con units para obtener symbol
            "required_quantity": comp.quantity * multiplier,
            "notes": comp.notes,
        })

    return {
        "bundle_id": bundle.id,
        "bundle_code": bundle.code,
        "bundle_name": bundle.name,
        "multiplier": multiplier,
        "total_components": len(exploded),
        "components": exploded,
    }