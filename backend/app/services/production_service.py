"""Servicio de producción."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    Bundle,
    BundleComponent,
    ProductionOrder,
    ProductionPlan,
    Resource,
    StockLot,
    Tenant,
    Warehouse,
)
from app.services.inventory_service import register_movement
from app.models.operational.plan_item_annex import PlanItemAnnex


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
    - (Pendiente) Agrega el producto terminado (movimiento `in` del bundle).
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

    # 1. Obtener el bundle y sus componentes
    bundle = db.query(Bundle).filter(Bundle.id == order.bundle_id).first()
    if not bundle:
        raise HTTPException(404, "Bundle no encontrado")

    components = (
        db.query(BundleComponent)
        .filter(BundleComponent.bundle_id == bundle.id)
        .all()
    )

    if not components:
        raise HTTPException(400, "El bundle no tiene componentes definidos")

    # 2. Obtener el warehouse principal (asumimos que hay al menos uno activo)
    warehouse = (
        db.query(Warehouse).filter(Warehouse.is_active == True).first()
    )
    if not warehouse:
        raise HTTPException(
            400, "No hay un almacén activo para registrar movimientos"
        )

    # 3. Consumir cada componente
    for comp in components:
        qty_needed = comp.quantity * order.quantity

        # Verificar stock disponible en el warehouse
        total_stock = (
            db.query(func.coalesce(func.sum(StockLot.quantity), 0))
            .filter(StockLot.resource_id == comp.resource_id)
            .filter(StockLot.warehouse_id == warehouse.id)
            .scalar()
        )
        total_stock = Decimal(str(total_stock))

        if total_stock < qty_needed:
            resource_name = comp.resource.name if comp.resource else "Recurso desconocido"
            raise HTTPException(
                400,
                f"Stock insuficiente para el recurso {comp.resource_id}. "
                f"Necesitas {qty_needed}, tienes {total_stock}",
            )

        # Registrar movimiento de salida
        # Nota: register_movement espera lot_code, unit_cost, expiration, etc.
        # Para 'out', el lote se ignora (se calcula FIFO/LIFO), y unit_cost se calcula solo.
        register_movement(
            db=db,
            warehouse_id=warehouse.id,
            resource_id=comp.resource_id,
            lot_code=f"PROD-{order.code}",  # No se usa realmente para 'out'
            movement_type="out",
            quantity=qty_needed,
            unit_cost=None,
            expiration=None,
            reference=f"Producción {order.code}",
            notes=f"Consumo automático al completar orden {order.code}",
            created_by=None,  # Podrías pasar el user actual si lo tienes
        )

    # 4. (Pendiente) Ingresar el producto terminado.
    # TODO: Añadir un campo `output_resource_id` al modelo `Bundle`
    # y registrar aquí un movimiento `in` con ese recurso y la cantidad de la orden.
    # register_movement(
    #     db=db,
    #     warehouse_id=warehouse.id,
    #     resource_id=bundle.output_resource_id,
    #     lot_code=f"LOTE-{order.code}",
    #     movement_type="in",
    #     quantity=order.quantity,
    #     unit_cost=...,
    #     expiration=None,
    #     reference=f"Producción {order.code}",
    #     notes=f"Producto terminado de orden {order.code}",
    #     created_by=None,
    # )

    order.status = "completed"
    order.end_date = datetime.now(timezone.utc)
    db.flush()
    db.refresh(order)
    return order

def mark_exception(
    db: Session,
    tenant: Tenant,
    order_id: UUID,
    exception_type: str,
    notes: str | None = None,
    actual_quantity: Decimal | None = None,
) -> dict:
    """Marca una orden de producción con una excepción.

    Tipos:
    - not_executed: no se ejecutó. Se repone todo el material preparado.
    - partial: se ejecutó parcialmente. Se repone el material no consumido.
    - with_deviation: se ejecutó con desviación. Se registra la cantidad real.
    """
    _set_tenant_schema(db, tenant)

    if exception_type not in ("not_executed", "partial", "with_deviation"):
        raise HTTPException(400, f"Tipo de excepción inválido: {exception_type}")

    order = (
        db.query(ProductionOrder)
        .filter(ProductionOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(404, "Orden de producción no encontrada")

    if order.status not in ("in_progress", "planned"):
        raise HTTPException(
            400,
            f"No se puede marcar excepción en estado {order.status}",
        )

    # Mapear tipo de excepción a estado
    status_map = {
        "not_executed": "not_executed",
        "partial": "partial",
        "with_deviation": "with_deviation",
    }
    order.status = status_map[exception_type]
    order.exception_type = exception_type
    order.exception_notes = notes
    order.end_date = datetime.now(timezone.utc)

    restored_quantity = Decimal("0")

    # Si es 'not_executed', reponer todo el material
    if exception_type == "not_executed":
        bundle = db.query(Bundle).filter(Bundle.id == order.bundle_id).first()
        if bundle:
            components = (
                db.query(BundleComponent)
                .filter(BundleComponent.bundle_id == bundle.id)
                .all()
            )
            warehouse = (
                db.query(Warehouse).filter(Warehouse.is_active == True).first()
            )
            if warehouse:
                for comp in components:
                    qty_to_restore = comp.quantity * order.quantity
                    if qty_to_restore > 0:
                        register_movement(
                            db=db,
                            warehouse_id=warehouse.id,
                            resource_id=comp.resource_id,
                            lot_code=f"RESTORE-{order.code}",
                            movement_type="in",
                            quantity=qty_to_restore,
                            unit_cost=None,
                            expiration=None,
                            reference=f"Reposición {order.code}",
                            notes=f"Reposición por no ejecución de orden {order.code}",
                            created_by=None,
                        )
                        restored_quantity += qty_to_restore

def add_annex(
    db: Session,
    tenant: Tenant,
    order_id: UUID,
    annex_type: str,
    resource_id: UUID | None = None,
    quantity: Decimal | None = None,
    notes: str | None = None,
) -> dict:
    """Registra un anexo en una orden de producción en progreso."""
    _set_tenant_schema(db, tenant)

    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "Orden de producción no encontrada")

    if order.status != "in_progress":
        raise HTTPException(
            400,
            f"Solo se pueden añadir anexos a órdenes en progreso. Estado actual: {order.status}",
        )

    # Crear el anexo
    annex = PlanItemAnnex(
        production_order_id=order.id,
        annex_type=annex_type,
        resource_id=resource_id,
        quantity=quantity,
        notes=notes,
    )
    db.add(annex)
    db.flush()
    db.refresh(annex)

    # Preparamos la respuesta para el frontend (buscando el nombre del recurso)
    resource_name = None
    if annex.resource_id:
        res = db.query(Resource).filter(Resource.id == annex.resource_id).first()
        if res:
            resource_name = res.name

    return {
        "id": annex.id,
        "production_order_id": annex.production_order_id,
        "annex_type": annex.annex_type,
        "resource_id": annex.resource_id,
        "resource_name": resource_name,
        "quantity": annex.quantity,
        "notes": annex.notes,
    }

    db.flush()
    db.refresh(order)

    return {
        "order_id": order.id,
        "order_code": order.code,
        "exception_type": exception_type,
        "message": f"Orden {order.code} marcada como {exception_type}.",
        "restored_quantity": restored_quantity,
    }