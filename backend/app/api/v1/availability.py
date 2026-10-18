# app/api/v1/availability.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_tenant
from app.models import Tenant
from app.schemas.availability import (
    AvailabilityRequest,
    AvailabilityResponse,
    BundleAvailabilityRequest,
    BundleAvailabilityResponse,
)
from app.services import availability_service

router = APIRouter(prefix="/availability", tags=["availability"])

@router.post("/check", response_model=AvailabilityResponse)
def check_single_resource(
    request: AvailabilityRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Verifica la disponibilidad de un recurso suelto.
    """
    try:
        return availability_service.check_availability(
            db=db,
            resource_id=request.resource_id,
            required_quantity=request.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/check-bundle", response_model=BundleAvailabilityResponse)
def check_bundle(
    request: BundleAvailabilityRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Verifica la disponibilidad de un bundle explotado.
    """
    try:
        return availability_service.check_bundle_availability(
            db=db,
            bundle_id=request.bundle_id,
            multiplier=request.multiplier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))