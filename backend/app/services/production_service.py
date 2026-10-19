"""Servicio de producción."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    Bundle,
    BundleComponent,
    ProductionOrder,
    ProductionPlan,
    Tenant,
)
from app.services.inventory_service import register_movement


def _set_tenant_schema(db: Session, tenant: Tenant) -> None:
    db.execute(text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))


def _generate_order_code(db: Session) -> str:
    """Genera un código único tipo PROD-2026-001."""
    year = datetime.now().year
    prefix = f"PROD-{year}-"
    last = (
        db.query(ProductionOrder)
        .filter(ProductionOrder.code.like(f"{prefix}%"))
        .order_by(ProductionOrder.code.desc())
        .first()
    )
    if last:
        try:
            num = int(last.code.replace(prefix, "")) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"{prefix}{num:04d}"


def start_production(
    db: Session, tenant: Tenant, order_id: UUID
) -> ProductionOrder:
    """Inicia una orden de producción."""
    _set_tenant_schema(db, tenant)

    order = (
        db.query(ProductionOrder)
        .filter(ProductionOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(404, "Orden de producción no encontrada")

    if order.status not in ("draft", "planned"):
        raise HTTPException(
            400, f"No se puede iniciar una orden en estado {order.status}"
        )

    order.status = "in_progress"
    order.start_date = datetime.now(timezone.utc)
    db.flush()
    db.refresh(order)
    return order


def complete_production(
    db: Session, tenant: Tenant, order_id: UUID
) -> ProductionOrder:
    """Completa una orden de producción.

    - Consume los materiales del bundle (movimientos `out`).
    - Agrega el producto terminado (movimiento `in` del bundle).
    """
    _set_tenant_schema(db, tenant)

    order = (
        db.query(ProductionOrder)
        .filter(ProductionOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(404, "Orden de producción no encontrada")

    if order.status != "in_progress":
        raise HTTPException(
            400, f"No se puede completar una orden en estado {order.status}"
        )

    # Obtener el bundle y sus componentes
    bundle = db.query(Bundle).filter(Bundle.id == order.bundle_id).first()
    if not bundle:
        raise HTTPException(404, "Bundle no encontrado")

    components = (
        db.query(BundleComponent)
        .filter(BundleComponent.bundle_id == bundle.id)
        .all()
    )

    # TODO: Consumir materiales (crear movimientos `out`) en los warehouses
    # Por ahora, solo marcamos la orden como completada.
    # En la próxima iteración, se implementa el consumo real.

    order.status = "completed"
    order.end_date = datetime.now(timezone.utc)
    db.flush()
    db.refresh(order)
    return order