"""Servicio de inventario: lógica de negocio para movimientos."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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
    - 'out' y 'loss' restan.
    - El lote se crea si no existe.
    - La cantidad del lote se actualiza en la misma transacción.
    """
    if movement_type not in MOVEMENT_TYPES:
        raise HTTPException(400, f"Tipo de movimiento inválido: {movement_type}")

    # Validar que existen
    _get_warehouse_or_404(db, warehouse_id)
    _get_resource_or_404(db, resource_id)

    # Obtener o crear el lote
    lot = _get_or_create_lot(
        db, warehouse_id, resource_id, lot_code, expiration, unit_cost
    )

    # Calcular nueva cantidad
    if movement_type in ("in", "adjust"):
        new_qty = lot.quantity + quantity
    else:  # out, loss
        new_qty = lot.quantity - quantity
        if new_qty < 0:
            raise HTTPException(
                400,
                f"Stock insuficiente: hay {lot.quantity}, se intenta sacar {quantity}",
            )

    # Actualizar lote
    lot.quantity = new_qty

    # Crear movimiento
    movement = Movement(
        warehouse_id=warehouse_id,
        resource_id=resource_id,
        lot_id=lot.id,
        movement_type=movement_type,
        quantity=quantity,
        unit_cost=unit_cost,
        reference=reference,
        notes=notes,
        created_by=created_by,
    )
    db.add(movement)
    db.flush()
    return movement