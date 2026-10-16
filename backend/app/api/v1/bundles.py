"""CRUD de Bundles (por tenant) + endpoint de explosión."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import Bundle, BundleComponent, Resource, Tenant
from app.schemas.bundle import (
    BundleComponentResponse,
    BundleCreate,
    BundleExplodeResponse,
    BundleListResponse,
    BundleResponse,
    BundleUpdate,
)
from app.services.bundle_service import explode_bundle

router = APIRouter(prefix="/bundles", tags=["bundles"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_bundle_or_404(db: Session, bundle_id: UUID) -> Bundle:
    b = (
        db.query(Bundle)
        .options(joinedload(Bundle.components))
        .filter(Bundle.id == bundle_id)
        .first()
    )
    if not b:
        raise HTTPException(404, "Bundle no encontrado")
    return b


def _build_component_response(
    db: Session, comp: BundleComponent
) -> BundleComponentResponse:
    resource = db.query(Resource).filter(Resource.id == comp.resource_id).first()
    return BundleComponentResponse(
        resource_id=comp.resource_id,
        resource_name=resource.name if resource else "",
        resource_unit_symbol=None,
        quantity=comp.quantity,
        notes=comp.notes,
    )


def _build_response(db: Session, bundle: Bundle) -> BundleResponse:
    return BundleResponse(
        id=bundle.id,
        code=bundle.code,
        name=bundle.name,
        description=bundle.description,
        category_id=bundle.category_id,
        is_active=bundle.is_active,
        created_at=bundle.created_at,
        updated_at=bundle.updated_at,
        components=[
            _build_component_response(db, c) for c in bundle.components
        ],
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=BundleListResponse)
def list_bundles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: bool | None = None,
    search: str | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    query = db.query(Bundle).options(joinedload(Bundle.components))
    if is_active is not None:
        query = query.filter(Bundle.is_active == is_active)
    if search:
        query = query.filter(Bundle.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Bundle.name).offset(skip).limit(limit).all()
    return BundleListResponse(
        items=[_build_response(db, b) for b in items],
        total=total,
    )


@router.get("/{bundle_id}", response_model=BundleResponse)
def get_bundle(
    bundle_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    b = _get_bundle_or_404(db, bundle_id)
    return _build_response(db, b)


@router.post("", response_model=BundleResponse, status_code=status.HTTP_201_CREATED)
def create_bundle(
    data: BundleCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    existing = db.query(Bundle).filter(Bundle.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe un bundle con ese código")

    bundle_data = data.model_dump(exclude={"components"})
    bundle = Bundle(**bundle_data)
    db.add(bundle)
    db.flush()

    for comp in data.components:
        resource = db.query(Resource).filter(Resource.id == comp.resource_id).first()
        if not resource:
            raise HTTPException(400, f"Recurso no encontrado: {comp.resource_id}")
        db.add(
            BundleComponent(
                bundle_id=bundle.id,
                resource_id=comp.resource_id,
                quantity=comp.quantity,
                notes=comp.notes,
            )
        )

    db.flush()
    db.refresh(bundle)
    bundle = _get_bundle_or_404(db, bundle.id)
    return _build_response(db, bundle)


@router.put("/{bundle_id}", response_model=BundleResponse)
def update_bundle(
    bundle_id: UUID,
    data: BundleUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    bundle = _get_bundle_or_404(db, bundle_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(bundle, key, value)
    db.flush()
    db.refresh(bundle)
    bundle = _get_bundle_or_404(db, bundle_id)
    return _build_response(db, bundle)


@router.delete("/{bundle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bundle(
    bundle_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    bundle = _get_bundle_or_404(db, bundle_id)
    bundle.is_active = False
    db.flush()


# ---------------------------------------------------------------------------
# Componentes del bundle
# ---------------------------------------------------------------------------

@router.post(
    "/{bundle_id}/components",
    response_model=BundleComponentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_bundle_component(
    bundle_id: UUID,
    data: dict,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Añade un componente a un bundle."""
    from uuid import UUID as UUIDType

    _get_bundle_or_404(db, bundle_id)
    resource_id = data.get("resource_id")
    quantity = data.get("quantity")
    if not resource_id or quantity is None:
        raise HTTPException(400, "resource_id y quantity son requeridos")

    try:
        resource_uuid = UUIDType(resource_id)
        quantity_decimal = Decimal(str(quantity))
    except (ValueError, TypeError):
        raise HTTPException(400, "Datos inválidos")

    if quantity_decimal <= 0:
        raise HTTPException(400, "La cantidad debe ser > 0")

    resource = db.query(Resource).filter(Resource.id == resource_uuid).first()
    if not resource:
        raise HTTPException(400, "Recurso no encontrado")

    existing = (
        db.query(BundleComponent)
        .filter(
            BundleComponent.bundle_id == bundle_id,
            BundleComponent.resource_id == resource_uuid,
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "El recurso ya está en el bundle")

    comp = BundleComponent(
        bundle_id=bundle_id,
        resource_id=resource_uuid,
        quantity=quantity_decimal,
        notes=data.get("notes"),
    )
    db.add(comp)
    db.flush()
    db.refresh(comp)
    return _build_component_response(db, comp)


@router.put(
    "/{bundle_id}/components/{resource_id}",
    response_model=BundleComponentResponse,
)
def update_bundle_component(
    bundle_id: UUID,
    resource_id: UUID,
    data: dict,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza un componente (cantidad, notas)."""
    comp = (
        db.query(BundleComponent)
        .filter(
            BundleComponent.bundle_id == bundle_id,
            BundleComponent.resource_id == resource_id,
        )
        .first()
    )
    if not comp:
        raise HTTPException(404, "Componente no encontrado")

    if "quantity" in data and data["quantity"] is not None:
        try:
            q = Decimal(str(data["quantity"]))
            if q <= 0:
                raise HTTPException(400, "La cantidad debe ser > 0")
            comp.quantity = q
        except (ValueError, TypeError):
            raise HTTPException(400, "Cantidad inválida")
    if "notes" in data:
        comp.notes = data["notes"]

    db.flush()
    db.refresh(comp)
    return _build_component_response(db, comp)


@router.delete(
    "/{bundle_id}/components/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_bundle_component(
    bundle_id: UUID,
    resource_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    comp = (
        db.query(BundleComponent)
        .filter(
            BundleComponent.bundle_id == bundle_id,
            BundleComponent.resource_id == resource_id,
        )
        .first()
    )
    if not comp:
        raise HTTPException(404, "Componente no encontrado")
    db.delete(comp)
    db.flush()


# ---------------------------------------------------------------------------
# Explosión del bundle
# ---------------------------------------------------------------------------

@router.post("/{bundle_id}/explode", response_model=BundleExplodeResponse)
def explode(
    bundle_id: UUID,
    multiplier: Decimal = 1,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Explota un bundle: devuelve la lista de recursos requeridos.

    El `multiplier` (default: 1) indica cuántas veces se multiplica el bundle.
    Ejemplo: si el bundle es "lote 100 unidades" y quieres 500 unidades,
    multiplier=5.
    """
    result = explode_bundle(db, bundle_id, multiplier)
    return BundleExplodeResponse(**result)