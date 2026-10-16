"""CRUD de Suppliers (por tenant)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    Currency,
    Resource,
    Supplier,
    SupplierResource,
    Tenant,
)
from app.schemas.supplier import (
    SupplierCreate,
    SupplierListResponse,
    SupplierResourceResponse,
    SupplierResourceUpdate,
    SupplierResponse,
    SupplierUpdate,
)

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_supplier_or_404(db: Session, supplier_id: UUID) -> Supplier:
    s = (
        db.query(Supplier)
        .options(joinedload(Supplier.resources))
        .filter(Supplier.id == supplier_id)
        .first()
    )
    if not s:
        raise HTTPException(404, "Proveedor no encontrado")
    return s


def _build_resource_response(db: Session, sr: SupplierResource) -> SupplierResourceResponse:
    resource = db.query(Resource).filter(Resource.id == sr.resource_id).first()
    currency = (
        db.query(Currency).filter(Currency.id == sr.currency_id).first()
        if sr.currency_id
        else None
    )
    return SupplierResourceResponse(
        resource_id=sr.resource_id,
        resource_name=resource.name if resource else "",
        unit_price=sr.unit_price,
        currency_id=sr.currency_id,
        currency_code=currency.code if currency else None,
        lead_time_days=sr.lead_time_days,
        min_quantity=sr.min_quantity,
        valid_until=sr.valid_until,
        notes=sr.notes,
    )


def _build_response(db: Session, supplier: Supplier) -> SupplierResponse:
    return SupplierResponse(
        id=supplier.id,
        code=supplier.code,
        name=supplier.name,
        tax_id=supplier.tax_id,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        contact_name=supplier.contact_name,
        notes=supplier.notes,
        is_active=supplier.is_active,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
        resources=[_build_resource_response(db, sr) for sr in supplier.resources],
    )


# ---------------------------------------------------------------------------
# Endpoints Supplier
# ---------------------------------------------------------------------------

@router.get("", response_model=SupplierListResponse)
def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: bool | None = None,
    search: str | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    query = db.query(Supplier).options(joinedload(Supplier.resources))
    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Supplier.name).offset(skip).limit(limit).all()
    return SupplierListResponse(
        items=[_build_response(db, s) for s in items],
        total=total,
    )


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    s = _get_supplier_or_404(db, supplier_id)
    return _build_response(db, s)


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    data: SupplierCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    existing = db.query(Supplier).filter(Supplier.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe un proveedor con ese código")

    supplier_data = data.model_dump(exclude={"resources"})
    supplier = Supplier(**supplier_data)
    db.add(supplier)
    db.flush()

    for r in data.resources:
        resource = db.query(Resource).filter(Resource.id == r.resource_id).first()
        if not resource:
            raise HTTPException(400, f"Recurso no encontrado: {r.resource_id}")
        db.add(
            SupplierResource(
                supplier_id=supplier.id,
                resource_id=r.resource_id,
                unit_price=r.unit_price,
                currency_id=r.currency_id,
                lead_time_days=r.lead_time_days,
                min_quantity=r.min_quantity,
                valid_until=r.valid_until,
                notes=r.notes,
            )
        )

    db.flush()
    db.refresh(supplier)
    supplier = _get_supplier_or_404(db, supplier.id)
    return _build_response(db, supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: UUID,
    data: SupplierUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    supplier = _get_supplier_or_404(db, supplier_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, key, value)
    db.flush()
    db.refresh(supplier)
    supplier = _get_supplier_or_404(db, supplier_id)
    return _build_response(db, supplier)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    supplier = _get_supplier_or_404(db, supplier_id)
    supplier.is_active = False
    db.flush()


# ---------------------------------------------------------------------------
# Endpoints de recursos del proveedor
# ---------------------------------------------------------------------------

@router.post(
    "/{supplier_id}/resources",
    response_model=SupplierResourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_supplier_resource(
    supplier_id: UUID,
    data: dict,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    from uuid import UUID as UUIDType

    _get_supplier_or_404(db, supplier_id)
    resource_id = data.get("resource_id")
    if not resource_id:
        raise HTTPException(400, "resource_id es requerido")

    try:
        resource_uuid = UUIDType(resource_id)
    except (ValueError, TypeError):
        raise HTTPException(400, "resource_id inválido")

    resource = db.query(Resource).filter(Resource.id == resource_uuid).first()
    if not resource:
        raise HTTPException(400, "Recurso no encontrado")

    existing = (
        db.query(SupplierResource)
        .filter(
            SupplierResource.supplier_id == supplier_id,
            SupplierResource.resource_id == resource_uuid,
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "El recurso ya está asociado")

    sr = SupplierResource(
        supplier_id=supplier_id,
        resource_id=resource_uuid,
        unit_price=data.get("unit_price"),
        currency_id=data.get("currency_id"),
        lead_time_days=data.get("lead_time_days"),
        min_quantity=data.get("min_quantity"),
        valid_until=data.get("valid_until"),
        notes=data.get("notes"),
    )
    db.add(sr)
    db.flush()
    db.refresh(sr)
    return _build_resource_response(db, sr)


@router.put(
    "/{supplier_id}/resources/{resource_id}",
    response_model=SupplierResourceResponse,
)
def update_supplier_resource(
    supplier_id: UUID,
    resource_id: UUID,
    data: SupplierResourceUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    sr = (
        db.query(SupplierResource)
        .filter(
            SupplierResource.supplier_id == supplier_id,
            SupplierResource.resource_id == resource_id,
        )
        .first()
    )
    if not sr:
        raise HTTPException(404, "Relación no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(sr, key, value)
    db.flush()
    db.refresh(sr)
    return _build_resource_response(db, sr)


@router.delete(
    "/{supplier_id}/resources/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_supplier_resource(
    supplier_id: UUID,
    resource_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    sr = (
        db.query(SupplierResource)
        .filter(
            SupplierResource.supplier_id == supplier_id,
            SupplierResource.resource_id == resource_id,
        )
        .first()
    )
    if not sr:
        raise HTTPException(404, "Relación no encontrada")
    db.delete(sr)
    db.flush()