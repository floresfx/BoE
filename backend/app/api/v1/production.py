"""Endpoints de producción (MPS)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.api.permissions import require_permission
from app.core.database import get_db
from app.models import (
    Bundle,
    ProductionOrder,
    ProductionPlan,
    PRODUCTION_ORDER_STATUSES,
    PRODUCTION_PLAN_STATUSES,
    Tenant,
)
from app.schemas.production import (
    GenerateOrdersRequest,
    ProductionOrderCreate,
    ProductionOrderListResponse,
    ProductionOrderResponse,
    ProductionPlanCreate,
    ProductionPlanListResponse,
    ProductionPlanResponse,
    ProductionPlanUpdate,
)
from app.services.production_service import (
    _generate_order_code,
    complete_production,
    start_production,
)

router = APIRouter(prefix="/production", tags=["production"])


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------

@router.get("/plans", response_model=ProductionPlanListResponse)
def list_plans(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    plans = db.query(ProductionPlan).all()
    return ProductionPlanListResponse(
        items=[ProductionPlanResponse.model_validate(p) for p in plans],
        total=len(plans),
    )


@router.post(
    "/plans",
    response_model=ProductionPlanResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("production", "crear"))],
)
def create_plan(
    data: ProductionPlanCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    plan = ProductionPlan(**data.model_dump())
    db.add(plan)
    db.flush()
    db.refresh(plan)
    return ProductionPlanResponse.model_validate(plan)


@router.put(
    "/plans/{plan_id}",
    response_model=ProductionPlanResponse,
    dependencies=[Depends(require_permission("production", "editar"))],
)
def update_plan(
    plan_id: UUID,
    data: ProductionPlanUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] not in PRODUCTION_PLAN_STATUSES:
        raise HTTPException(400, f"Estado inválido: {update_data['status']}")

    for key, value in update_data.items():
        setattr(plan, key, value)

    db.flush()
    db.refresh(plan)
    return ProductionPlanResponse.model_validate(plan)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@router.get("/orders", response_model=ProductionOrderListResponse)
def list_orders(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    orders = db.query(ProductionOrder).all()
    result = []
    for o in orders:
        bundle = db.query(Bundle).filter(Bundle.id == o.bundle_id).first()
        result.append(
            ProductionOrderResponse(
                id=o.id,
                code=o.code,
                plan_id=o.plan_id,
                bundle_id=o.bundle_id,
                bundle_name=bundle.name if bundle else "",
                quantity=o.quantity,
                status=o.status,
                start_date=o.start_date,
                end_date=o.end_date,
                notes=o.notes,
                created_at=o.created_at,
                updated_at=o.updated_at,
            )
        )
    return ProductionOrderListResponse(items=result, total=len(result))


@router.post(
    "/orders",
    response_model=ProductionOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("production", "crear"))],
)
def create_order(
    data: ProductionOrderCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    bundle = db.query(Bundle).filter(Bundle.id == data.bundle_id).first()
    if not bundle:
        raise HTTPException(404, "Bundle no encontrado")

    code = data.code or _generate_order_code(db)
    order = ProductionOrder(
        code=code,
        plan_id=data.plan_id,
        bundle_id=data.bundle_id,
        quantity=data.quantity,
        notes=data.notes,
        status="draft",
    )
    db.add(order)
    db.flush()
    db.refresh(order)
    return ProductionOrderResponse(
        id=order.id,
        code=order.code,
        plan_id=order.plan_id,
        bundle_id=order.bundle_id,
        bundle_name=bundle.name,
        quantity=order.quantity,
        status=order.status,
        start_date=order.start_date,
        end_date=order.end_date,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post(
    "/orders/{order_id}/start",
    response_model=ProductionOrderResponse,
    dependencies=[Depends(require_permission("production", "editar"))],
)
def start_order(
    order_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    order = start_production(db, current_tenant, order_id)
    bundle = db.query(Bundle).filter(Bundle.id == order.bundle_id).first()
    return ProductionOrderResponse(
        id=order.id,
        code=order.code,
        plan_id=order.plan_id,
        bundle_id=order.bundle_id,
        bundle_name=bundle.name if bundle else "",
        quantity=order.quantity,
        status=order.status,
        start_date=order.start_date,
        end_date=order.end_date,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post(
    "/orders/{order_id}/complete",
    response_model=ProductionOrderResponse,
    dependencies=[Depends(require_permission("production", "editar"))],
)
def complete_order(
    order_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    order = complete_production(db, current_tenant, order_id)
    bundle = db.query(Bundle).filter(Bundle.id == order.bundle_id).first()
    return ProductionOrderResponse(
        id=order.id,
        code=order.code,
        plan_id=order.plan_id,
        bundle_id=order.bundle_id,
        bundle_name=bundle.name if bundle else "",
        quantity=order.quantity,
        status=order.status,
        start_date=order.start_date,
        end_date=order.end_date,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )

@router.put(
    "/orders/{order_id}/status",
    response_model=ProductionOrderResponse,
    dependencies=[Depends(require_permission("production", "editar"))],
)
def update_order_status(
    order_id: UUID,
    data: dict,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Cambia el estado de una orden de producción."""
    from app.models import PRODUCTION_ORDER_STATUSES

    order = (
        db.query(ProductionOrder)
        .filter(ProductionOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(404, "Orden no encontrada")

    new_status = data.get("status")
    if new_status not in PRODUCTION_ORDER_STATUSES:
        raise HTTPException(400, f"Estado inválido: {new_status}")

    order.status = new_status
    db.flush()
    db.refresh(order)

    bundle = db.query(Bundle).filter(Bundle.id == order.bundle_id).first()
    return ProductionOrderResponse(
        id=order.id,
        code=order.code,
        plan_id=order.plan_id,
        bundle_id=order.bundle_id,
        bundle_name=bundle.name if bundle else "",
        quantity=order.quantity,
        status=order.status,
        start_date=order.start_date,
        end_date=order.end_date,
        notes=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )