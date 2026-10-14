"""CRUD de recursos operativos (Fase 2).

Todos los endpoints requieren autenticación + tenant.
El `SET LOCAL search_path` lo aplica `get_current_tenant`.

Novedades Fase 2:
- category_id, subcategory_id, base_unit_id (FKs a datos maestros)
- attributes inline en create
- taxes inline en create
- Response con attributes y taxes anidados
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.services.plan_service import check_plan_limit
from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    Attribute,
    Category,
    Resource,
    ResourceAttribute,
    ResourceTax,
    RESOURCE_TYPES,
    Subcategory,
    Tax,
    Tenant,
    Unit,
)
from app.schemas.resource import (
    ResourceCreate,
    ResourceListResponse,
    ResourceResponse,
    ResourceUpdate,
)

from app.services.plan_service import check_plan_limit

router = APIRouter(prefix="/resources", tags=["resources"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_resource_or_404(db: Session, resource_id: UUID) -> Resource:
    """Busca un recurso en el schema del tenant (vía search_path)."""
    resource = (
        db.query(Resource)
        .options(
            joinedload(Resource.attributes),
            joinedload(Resource.taxes),
        )
        .filter(Resource.id == resource_id)
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado",
        )
    return resource


def _validate_fk_exists(db: Session, model, id_value: UUID, name: str) -> None:
    """Valida que una FK exista. Lanza 400 si no."""
    exists = db.query(model).filter(model.id == id_value).first()
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{name} no encontrado: {id_value}",
        )


def _build_resource_response(
    db: Session, resource: Resource
) -> ResourceResponse:
    """Construye la respuesta enriquecida con datos de attributes y taxes."""
    # Cargar atributos con datos maestros
    attributes_data = []
    for ra in resource.attributes:
        attr = db.query(Attribute).filter(Attribute.id == ra.attribute_id).first()
        if attr:
            attributes_data.append({
                "attribute_id": ra.attribute_id,
                "attribute_code": attr.code,
                "attribute_name": attr.name,
                "value": ra.value,
            })

    # Cargar taxes con datos maestros
    taxes_data = []
    for rt in resource.taxes:
        tax = db.query(Tax).filter(Tax.id == rt.tax_id).first()
        if tax:
            taxes_data.append({
                "tax_id": rt.tax_id,
                "tax_code": tax.code,
                "tax_name": tax.name,
                "tax_rate": tax.rate,
            })

    return ResourceResponse(
        id=resource.id,
        name=resource.name,
        resource_type=resource.resource_type,
        category_id=resource.category_id,
        subcategory_id=resource.subcategory_id,
        base_unit_id=resource.base_unit_id,
        cost=resource.cost,
        is_active=resource.is_active,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
        attributes=attributes_data,
        taxes=taxes_data,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=ResourceListResponse)
def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    resource_type: str | None = None,
    category_id: UUID | None = None,
    subcategory_id: UUID | None = None,
    search: str | None = None,
    is_active: bool | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista recursos del tenant actual con filtros opcionales."""
    query = db.query(Resource).options(
        joinedload(Resource.attributes),
        joinedload(Resource.taxes),
    )

    if resource_type:
        if resource_type not in RESOURCE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"resource_type inválido: {resource_type}",
            )
        query = query.filter(Resource.resource_type == resource_type)

    if category_id:
        query = query.filter(Resource.category_id == category_id)

    if subcategory_id:
        query = query.filter(Resource.subcategory_id == subcategory_id)

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
        items=[_build_resource_response(db, r) for r in items],
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
    return _build_resource_response(db, resource)


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

    Usa flush (no commit) para mantener viva la transacción con su
    search_path. El commit lo hace get_db al terminar el request.
    """
    # Verificar límite del plan
    check_plan_limit(db, current_tenant, "recursos", Resource)

    # Validar FKs
    _validate_fk_exists(db, Unit, data.base_unit_id, "Unidad")
    if data.category_id:
        _validate_fk_exists(db, Category, data.category_id, "Categoría")
    if data.subcategory_id:
        _validate_fk_exists(db, Subcategory, data.subcategory_id, "Subcategoría")

    # Nombre único por tipo dentro del tenant
    existing = (
        db.query(Resource)
        .filter(
            Resource.name == data.name,
            Resource.resource_type == data.resource_type,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un recurso con ese nombre y tipo",
        )

    # Crear el recurso (sin atributos ni taxes todavía)
    resource_data = data.model_dump(exclude={"attributes", "taxes"})
    resource = Resource(**resource_data)
    db.add(resource)
    db.flush()

    # Crear los atributos inline
    for attr_inline in data.attributes:
        _validate_fk_exists(db, Attribute, attr_inline.attribute_id, "Atributo")
        db.add(
            ResourceAttribute(
                resource_id=resource.id,
                attribute_id=attr_inline.attribute_id,
                value=attr_inline.value,
            )
        )

    # Crear los taxes inline
    for tax_inline in data.taxes:
        _validate_fk_exists(db, Tax, tax_inline.tax_id, "Impuesto")
        db.add(
            ResourceTax(
                resource_id=resource.id,
                tax_id=tax_inline.tax_id,
            )
        )

    db.flush()
    db.refresh(resource)

    # Recargar con atributos y taxes
    resource = _get_resource_or_404(db, resource.id)
    return _build_resource_response(db, resource)


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza un recurso.

    Los atributos e impuestos se gestionan con endpoints dedicados.
    """
    resource = _get_resource_or_404(db, resource_id)

    update_data = data.model_dump(exclude_unset=True)

    # Validar FKs si vienen
    if "base_unit_id" in update_data:
        _validate_fk_exists(db, Unit, update_data["base_unit_id"], "Unidad")
    if "category_id" in update_data and update_data["category_id"]:
        _validate_fk_exists(db, Category, update_data["category_id"], "Categoría")
    if "subcategory_id" in update_data and update_data["subcategory_id"]:
        _validate_fk_exists(db, Subcategory, update_data["subcategory_id"], "Subcategoría")

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

    db.flush()
    db.refresh(resource)

    # Recargar con atributos y taxes
    resource = _get_resource_or_404(db, resource_id)
    return _build_resource_response(db, resource)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Soft delete: marca is_active=False."""
    resource = _get_resource_or_404(db, resource_id)
    resource.is_active = False
    db.flush()