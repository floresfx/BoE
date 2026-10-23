"""Endpoints de órdenes de compra."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.api.permissions import require_permission
from app.core.database import get_db
from app.models import Tenant
from app.schemas.purchase_order import (
    PurchaseOrderListResponse,
    PurchaseOrderResponse,
)
from app.services.purchase_order_service import (
    confirm_order,
    generate_order_from_quote,
    list_orders,
    receive_order,
)

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


@router.get("", response_model=PurchaseOrderListResponse)
def list_purchase_orders(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista todas las órdenes de compra."""
    items = list_orders(db, current_tenant)
    return PurchaseOrderListResponse(items=items, total=len(items))


@router.post(
    "/from-quote",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("purchase_request", "aprobar"))],
)
def generate_from_quote(
    request_id: UUID,
    quote_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Genera una orden de compra desde una cotización aceptada."""
    return generate_order_from_quote(db, current_tenant, request_id, quote_id)


@router.post(
    "/{order_id}/confirm",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission("purchase_request", "aprobar"))],
)
def confirm_purchase_order(
    order_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Confirma una orden de compra (draft → confirmed)."""
    return confirm_order(db, current_tenant, order_id)


@router.post(
    "/{order_id}/receive",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission("purchase_request", "aprobar"))],
)
def receive_purchase_order(
    order_id: UUID,
    warehouse_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Recibe la mercancía de una orden confirmada."""
    return receive_order(db, current_tenant, order_id, warehouse_id)