"""Endpoints de movimientos de inventario."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import Movement, Tenant
from app.schemas.movement import (
    MovementCreate,
    MovementListResponse,
    MovementResponse,
)
from app.services.inventory_service import register_movement

router = APIRouter(prefix="/movements", tags=["movements"])


@router.get("", response_model=MovementListResponse)
def list_movements(
    skip: int = 0,
    limit: int = 100,
    warehouse_id: UUID | None = None,
    resource_id: UUID | None = None,
    movement_type: str | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    query = db.query(Movement)
    if warehouse_id:
        query = query.filter(Movement.warehouse_id == warehouse_id)
    if resource_id:
        query = query.filter(Movement.resource_id == resource_id)
    if movement_type:
        query = query.filter(Movement.movement_type == movement_type)
    total = query.count()
    items = (
        query.order_by(Movement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return MovementListResponse(
        items=[MovementResponse.model_validate(m) for m in items],
        total=total,
    )


@router.post("", response_model=MovementResponse, status_code=201)
def create_movement(
    data: MovementCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Registra un movimiento. Actualiza el stock del lote automáticamente."""
    movement = register_movement(
        db=db,
        warehouse_id=data.warehouse_id,
        resource_id=data.resource_id,
        lot_code=data.lot_code,
        movement_type=data.movement_type,
        quantity=data.quantity,
        unit_cost=data.unit_cost,
        expiration=data.expiration,
        reference=data.reference,
        notes=data.notes,
        created_by=None,  # TODO: obtener current_user.id
    )
    db.refresh(movement)
    return MovementResponse.model_validate(movement)