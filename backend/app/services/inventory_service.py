"""Servicio de inventario: lógica de negocio para movimientos."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Tenant

from app.models import (
    Movement,
    MOVEMENT_TYPES,
    Resource,
    StockLot,
    Warehouse,
)


def _get_warehouse_or_404(db: Session, warehouse_id: UUID) -> Warehouse:
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not w:
        raise HTTPException(404, "Warehouse no encontrado")
    return w


def _get_resource_or_404(db: Session, resource_id: UUID) -> Resource:
    r = db.query(Resource).filter(Resource.id == resource_id).first()
    if not r:
        raise HTTPException(404, "Recurso no encontrado")
    return r


def _get_or_create_lot(
    db: Session,
    warehouse_id: UUID,
    resource_id: UUID,
    lot_code: str,
    expiration: datetime | None = None,
    unit_cost: Decimal | None = None,
) -> StockLot:
    """Busca o crea un lote."""
    lot = (
        db.query(StockLot)
        .filter(
            StockLot.warehouse_id == warehouse_id,
            StockLot.resource_id == resource_id,
            StockLot.lot_code == lot_code,
        )
        .first()
    )
    if lot:
        return lot
    lot = StockLot(
        warehouse_id=warehouse_id,
        resource_id=resource_id,
        lot_code=lot_code,
        quantity=Decimal("0"),
        expiration=expiration,
        unit_cost=unit_cost,
        received_at=datetime.now(timezone.utc),
    )
    db.add(lot)
    db.flush()
    return lot

def _calculate_out_cost_fifo_lifo(
    db: Session,
    tenant: Tenant,
    resource_id: UUID,
    quantity: Decimal,
) -> Decimal:
    """
    Calcula el costo real de consumir `quantity` unidades del recurso,
    distribuyendo entre lotes según el método FIFO o LIFO del tenant.

    Devuelve el costo total consumido (promedio ponderado * quantity).
    También actualiza los lotes: reduce sus cantidades según el consumo.
    """
    method = tenant.inventory_costing_method or "fifo"

    # Obtener lotes con stock > 0, ordenados según el método
    order_clause = (
        "expiration ASC NULLS LAST, received_at ASC"
        if method == "fifo"
        else "received_at DESC"
    )

    lots = db.execute(
        text(f"""
            SELECT id, quantity, unit_cost, received_at
            FROM stock_lots
            WHERE resource_id = :resource_id AND quantity > 0
            ORDER BY {order_clause}
        """),
        {"resource_id": str(resource_id)},
    ).fetchall()

    if not lots:
        raise HTTPException(
            400,
            f"No hay stock del recurso {resource_id} para consumir",
        )

    remaining = quantity
    total_cost = Decimal("0")

    for lot in lots:
        if remaining <= 0:
            break

        lot_quantity = Decimal(str(lot.quantity))
        lot_cost = Decimal(str(lot.unit_cost)) if lot.unit_cost else Decimal("0")

        consume_from_lot = min(remaining, lot_quantity)

        # Calcular costo de esta porción
        total_cost += consume_from_lot * lot_cost

        # Actualizar el lote
        new_lot_quantity = lot_quantity - consume_from_lot
        db.execute(
            text("""
                UPDATE stock_lots
                SET quantity = :new_quantity
                WHERE id = :lot_id
            """),
            {"new_quantity": str(new_lot_quantity), "lot_id": str(lot.id)},
        )

        remaining -= consume_from_lot

    if remaining > 0:
        raise HTTPException(
            400,
            f"Stock insuficiente del recurso {resource_id}: "
            f"faltan {remaining} unidades",
        )

    return total_cost


def register_movement(
    db: Session,
    warehouse_id: UUID,
    resource_id: UUID,
    lot_code: str,
    movement_type: str,
    quantity: Decimal,
    unit_cost: Decimal | None,
    expiration: datetime | None,
    reference: str | None,
    notes: str | None,
    created_by: UUID | None,
) -> Movement:
    """Registra un movimiento y actualiza el stock del lote.

    Reglas:
    - 'in' y 'adjust' suman.
    - 'out' y 'loss' restan (con cálculo FIFO/LIFO).
    - El lote se crea si no existe (solo para 'in').
    """
    if movement_type not in MOVEMENT_TYPES:
        raise HTTPException(400, f"Tipo de movimiento inválido: {movement_type}")

    # Validar que existen
    _get_warehouse_or_404(db, warehouse_id)
    _get_resource_or_404(db, resource_id)

    # Obtener el tenant actual para conocer el método de costeo
    from app.models import Tenant
    current_schema = db.execute(text("SELECT current_schema()")).scalar()
    tenant = (
        db.query(Tenant)
        .filter(Tenant.schema_name == current_schema)
        .first()
    )
    if not tenant:
        tenant = db.query(Tenant).first()

    # Para 'out' y 'loss': calcular costo FIFO/LIFO
    if movement_type in ("out", "loss"):
        total_cost = _calculate_out_cost_fifo_lifo(
            db, tenant, resource_id, quantity
        )
        calculated_unit_cost = (
            total_cost / quantity if quantity > 0 else Decimal("0")
        )
    else:
        # Para 'in' y 'adjust': usar unit_cost proporcionado
        calculated_unit_cost = unit_cost

    # Obtener o crear el lote (solo para 'in' y 'adjust')
    if movement_type in ("in", "adjust"):
        lot = _get_or_create_lot(
            db, warehouse_id, resource_id, lot_code, expiration, unit_cost
        )
        new_qty = lot.quantity + quantity
        lot.quantity = new_qty
    else:
        # Para 'out' y 'loss': ya se actualizaron los lotes en el cálculo
        lot = None

    # Crear movimiento
    movement = Movement(
        warehouse_id=warehouse_id,
        resource_id=resource_id,
        lot_id=lot.id if lot else None,
        movement_type=movement_type,
        quantity=quantity,
        unit_cost=calculated_unit_cost,
        reference=reference,
        notes=notes,
        created_by=created_by,
    )
    db.add(movement)
    db.flush()
    return movement