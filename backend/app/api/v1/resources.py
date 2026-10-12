"""CRUD de recursos operativos.

Todos los endpoints requieren autenticación + tenant.
El `SET LOCAL search_path` lo aplica `get_current_tenant`.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import Resource, RESOURCE_TYPES, Tenant
from app.schemas.resource import (
    ResourceCreate,
    ResourceListResponse,
    ResourceResponse,
    ResourceUpdate,
)

router = APIRouter(prefix="/resources", tags=["resources"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_resource_or_404(db: Session, resource_id: UUID) -> Resource:
    """Busca un recurso en el schema del tenant (vía search_path)."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado",
        )
    return resource


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=ResourceListResponse)
def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    resource_type: str | None = None,
    category: str | None = None,
    search: str | None = None,
    is_active: bool | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista recursos del tenant actual con filtros opcionales."""
    query = db.query(Resource)

    if resource_type:
        if resource_type not in RESOURCE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"resource_type inválido: {resource_type}",
            )
        query = query.filter(Resource.resource_type == resource_type)

    if category:
        query = query.filter(Resource.category == category)

    if search:
        query = query.filter(Resource.name.ilike(f"%{search}%"))

    if is_active is not None:
        query = query.filter(Resource.is_active == is_active)

    total = query.count()
    items = (
        query.order_by(Resource.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return ResourceListResponse(
        items=[ResourceResponse.model_validate(r) for r in items],
        total=total,
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Obtiene un recurso por ID."""
    resource = _get_resource_or_404(db, resource_id)
    return ResourceResponse.model_validate(resource)


@router.post(
    "",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resource(
    data: ResourceCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Crea un recurso en el schema del tenant autenticado.

    El `search_path` ya está aplicado por get_current_tenant, así que
    la INSERT cae automáticamente en el schema correcto.
    """
    # Nombre único por tipo dentro del tenant
    existing = (
        db.query(Resource)
        .filter(Resource.name == data.name, Resource.resource_type == data.resource_type)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un recurso con ese nombre y tipo",
        )

    resource = Resource(**data.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return ResourceResponse.model_validate(resource)


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza un recurso."""
    resource = _get_resource_or_404(db, resource_id)

    update_data = data.model_dump(exclude_unset=True)

    # Si cambia el nombre, verificar unicidad
    if "name" in update_data and update_data["name"] != resource.name:
        existing = (
            db.query(Resource)
            .filter(
                Resource.name == update_data["name"],
                Resource.resource_type == resource.resource_type,
                Resource.id != resource.id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un recurso con ese nombre y tipo",
            )

    for key, value in update_data.items():
        setattr(resource, key, value)

    db.commit()
    db.refresh(resource)
    return ResourceResponse.model_validate(resource)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Soft delete: marca is_active=False.

    Ver DOCUMENTO 1 MPR, sección 14.4.
    """
    resource = _get_resource_or_404(db, resource_id)
    resource.is_active = False
    db.commit()