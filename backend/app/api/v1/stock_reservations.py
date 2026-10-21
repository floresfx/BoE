"""Endpoints de reservas de stock."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    StockReservation,
    Tenant,
    Warehouse,
    Resource,
    StockLot,
)
from app.schemas.stock_reservation import (
    StockReservationCreate,
    StockReservationListResponse,
    StockReservationResponse,
)

router = APIRouter(prefix="/stock/reservations", tags=["stock-reservations"])


@router.get("", response_model=StockReservationListResponse)
def list_reservations(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista todas las reservas de stock."""
    reservations = db.query(StockReservation).all()
    return StockReservationListResponse(
        items=[StockReservationResponse.model_validate(r) for r in reservations],
        total=len(reservations),
    )


@router.post("", response_model=StockReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: StockReservationCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Crea una reserva de stock."""
    # 1. Validar que el warehouse y el resource existen
    warehouse = db.query(Warehouse).filter(Warehouse.id == data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(404, "Almacén no encontrado")
    
    resource = db.query(Resource).filter(Resource.id == data.resource_id).first()
    if not resource:
        raise HTTPException(404, "Recurso no encontrado")

    # 2. Verificar stock disponible (stock total - reservas activas)
    from sqlalchemy import func
    total_stock = (
        db.query(func.sum(StockLot.quantity))
        .filter(StockLot.warehouse_id == data.warehouse_id)
        .filter(StockLot.resource_id == data.resource_id)
        .scalar()
    ) or 0

    total_reserved = (
        db.query(func.sum(StockReservation.quantity))
        .filter(StockReservation.warehouse_id == data.warehouse_id)
        .filter(StockReservation.resource_id == data.resource_id)
        .filter(StockReservation.status.in_(["pending", "confirmed"]))
        .scalar()
    ) or 0

    available = total_stock - total_reserved
    if data.quantity > available:
        raise HTTPException(
            400,
            f"Stock insuficiente. Disponible: {available}, Solicitado: {data.quantity}"
        )

    # 3. Crear la reserva
    reservation = StockReservation(
        warehouse_id=data.warehouse_id,
        resource_id=data.resource_id,
        quantity=data.quantity,
        reference=data.reference,
        notes=data.notes,
        needed_by=data.needed_by,
        status="pending",
    )
    db.add(reservation)
    db.flush()
    db.refresh(reservation)
    return StockReservationResponse.model_validate(reservation)


@router.post("/{reservation_id}/cancel", response_model=StockReservationResponse)
def cancel_reservation(
    reservation_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Cancela una reserva."""
    reservation = db.query(StockReservation).filter(StockReservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(404, "Reserva no encontrada")

    if reservation.status not in ("pending", "confirmed"):
        raise HTTPException(400, f"No se puede cancelar una reserva en estado {reservation.status}")

    reservation.status = "cancelled"
    db.flush()
    db.refresh(reservation)
    return StockReservationResponse.model_validate(reservation)