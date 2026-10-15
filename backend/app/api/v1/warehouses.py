"""CRUD de Warehouses (por tenant)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import Tenant, Warehouse
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseListResponse,
    WarehouseResponse,
    WarehouseUpdate,
)

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


def _get_or_404(db: Session, warehouse_id: UUID) -> Warehouse:
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not w:
        raise HTTPException(404, "Warehouse no encontrado")
    return w


@router.get("", response_model=WarehouseListResponse)
def list_warehouses(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    search: str | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    query = db.query(Warehouse)
    if is_active is not None:
        query = query.filter(Warehouse.is_active == is_active)
    if search:
        query = query.filter(Warehouse.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Warehouse.name).offset(skip).limit(limit).all()
    return WarehouseListResponse(
        items=[WarehouseResponse.model_validate(w) for w in items],
        total=total,
    )


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(
    warehouse_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return WarehouseResponse.model_validate(_get_or_404(db, warehouse_id))


@router.post(
    "", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED
)
def create_warehouse(
    data: WarehouseCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    existing = db.query(Warehouse).filter(Warehouse.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe un warehouse con ese código")
    w = Warehouse(**data.model_dump())
    db.add(w)
    db.flush()
    db.refresh(w)
    return WarehouseResponse.model_validate(w)


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: UUID,
    data: WarehouseUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    w = _get_or_404(db, warehouse_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(w, key, value)
    db.flush()
    db.refresh(w)
    return WarehouseResponse.model_validate(w)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(
    warehouse_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    w = _get_or_404(db, warehouse_id)
    w.is_active = False
    db.flush()