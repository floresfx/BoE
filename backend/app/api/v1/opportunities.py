"""Endpoints del Motor de Oportunidades (Matching Inverso)."""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import Tenant
from app.schemas.opportunity import OpportunityListResponse
from app.services.opportunity_service import find_opportunities

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=OpportunityListResponse)
def list_opportunities(
    min_coverage: Decimal = Query(Decimal("50.0"), ge=0, le=100),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Encuentra oportunidades: qué bundles se pueden producir con el stock actual.

    Ordenadas por margen estimado descendente.
    """
    items = find_opportunities(db, current_tenant, min_coverage)
    return OpportunityListResponse(items=items, total=len(items))