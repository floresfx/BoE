"""Endpoints dedicados para gestionar impuestos de un recurso.

Fase 2: N:M entre Resource y Tax.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    Resource,
    ResourceTax,
    Tax,
    Tenant,
)
from app.schemas.resource_tax import (
    ResourceTaxCreate,
    ResourceTaxResponse,
)

router = APIRouter(
    prefix="/resources/{resource_id}/taxes",
    tags=["resource-taxes"],
)


def _get_resource_or_404(db: Session, resource_id: UUID) -> Resource:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado",
        )
    return resource


def _get_resource_tax_or_404(
    db: Session, resource_id: UUID, tax_id: UUID
) -> ResourceTax:
    rt = (
        db.query(ResourceTax)
        .filter(
            ResourceTax.resource_id == resource_id,
            ResourceTax.tax_id == tax_id,
        )
        .first()
    )
    if not rt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impuesto de recurso no encontrado",
        )
    return rt


@router.get("", response_model=list[ResourceTaxResponse])
def list_resource_taxes(
    resource_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista los impuestos de un recurso."""
    _get_resource_or_404(db, resource_id)
    taxes = (
        db.query(ResourceTax)
        .filter(ResourceTax.resource_id == resource_id)
        .all()
    )
    return [ResourceTaxResponse.model_validate(t) for t in taxes]


@router.post(
    "",
    response_model=ResourceTaxResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resource_tax(
    resource_id: UUID,
    data: ResourceTaxCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Asigna un impuesto a un recurso."""
    _get_resource_or_404(db, resource_id)

    # Validar que el impuesto existe
    tax = db.query(Tax).filter(Tax.id == data.tax_id).first()
    if not tax:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impuesto no encontrado",
        )

    # Verificar que no esté ya asignado
    existing = (
        db.query(ResourceTax)
        .filter(
            ResourceTax.resource_id == resource_id,
            ResourceTax.tax_id == data.tax_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El impuesto ya está asignado a este recurso",
        )

    rt = ResourceTax(resource_id=resource_id, tax_id=data.tax_id)
    db.add(rt)
    db.flush()
    db.refresh(rt)
    return ResourceTaxResponse.model_validate(rt)


@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource_tax(
    resource_id: UUID,
    tax_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Quita un impuesto de un recurso."""
    rt = _get_resource_tax_or_404(db, resource_id, tax_id)
    db.delete(rt)
    db.flush()