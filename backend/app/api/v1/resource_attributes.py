"""Endpoints dedicados para gestionar atributos de un recurso.

Fase 2: N:M entre Resource y Attribute.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    Attribute,
    Resource,
    ResourceAttribute,
    Tenant,
)
from app.schemas.resource_attribute import (
    ResourceAttributeCreate,
    ResourceAttributeResponse,
    ResourceAttributeUpdate,
)

router = APIRouter(
    prefix="/resources/{resource_id}/attributes",
    tags=["resource-attributes"],
)


def _get_resource_or_404(db: Session, resource_id: UUID) -> Resource:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado",
        )
    return resource


def _get_resource_attribute_or_404(
    db: Session, resource_id: UUID, attribute_id: UUID
) -> ResourceAttribute:
    ra = (
        db.query(ResourceAttribute)
        .filter(
            ResourceAttribute.resource_id == resource_id,
            ResourceAttribute.attribute_id == attribute_id,
        )
        .first()
    )
    if not ra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atributo de recurso no encontrado",
        )
    return ra


@router.get("", response_model=list[ResourceAttributeResponse])
def list_resource_attributes(
    resource_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista los atributos de un recurso."""
    _get_resource_or_404(db, resource_id)
    attributes = (
        db.query(ResourceAttribute)
        .filter(ResourceAttribute.resource_id == resource_id)
        .all()
    )
    return [ResourceAttributeResponse.model_validate(a) for a in attributes]


@router.post(
    "",
    response_model=ResourceAttributeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resource_attribute(
    resource_id: UUID,
    data: ResourceAttributeCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Asigna un atributo a un recurso."""
    _get_resource_or_404(db, resource_id)

    # Validar que el atributo existe
    attribute = db.query(Attribute).filter(Attribute.id == data.attribute_id).first()
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atributo no encontrado",
        )

    # Verificar que no esté ya asignado
    existing = (
        db.query(ResourceAttribute)
        .filter(
            ResourceAttribute.resource_id == resource_id,
            ResourceAttribute.attribute_id == data.attribute_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El atributo ya está asignado a este recurso",
        )

    ra = ResourceAttribute(
        resource_id=resource_id,
        attribute_id=data.attribute_id,
        value=data.value,
    )
    db.add(ra)
    db.flush()
    db.refresh(ra)
    return ResourceAttributeResponse.model_validate(ra)


@router.put("/{attribute_id}", response_model=ResourceAttributeResponse)
def update_resource_attribute(
    resource_id: UUID,
    attribute_id: UUID,
    data: ResourceAttributeUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza el valor de un atributo de un recurso."""
    ra = _get_resource_attribute_or_404(db, resource_id, attribute_id)
    ra.value = data.value
    db.flush()
    db.refresh(ra)
    return ResourceAttributeResponse.model_validate(ra)


@router.delete("/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource_attribute(
    resource_id: UUID,
    attribute_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Quita un atributo de un recurso."""
    ra = _get_resource_attribute_or_404(db, resource_id, attribute_id)
    db.delete(ra)
    db.flush()