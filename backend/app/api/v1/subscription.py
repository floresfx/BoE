"""Endpoints de suscripción.

Permite al usuario seleccionar un plan después de registrarse.
Aplica la lógica de trial (14 días para planes MPR).
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import Plan, PlanFeature, Tenant
from app.schemas.subscription import (
    PlanSummary,
    SelectPlanRequest,
    SelectPlanResponse,
    SubscriptionInfo,
)

router = APIRouter(prefix="/subscription", tags=["subscription"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan_to_summary(db: Session, plan: Plan) -> PlanSummary:
    """Convierte un Plan a PlanSummary con features y limits."""
    from app.models import Currency, PlanLimit

    currency = db.query(Currency).filter(Currency.id == plan.currency_id).first()

    features = [
        pf.feature.code
        for pf in db.query(PlanFeature).filter(PlanFeature.plan_id == plan.id).all()
        if pf.feature
    ]

    limits = {}
    for pl in db.query(PlanLimit).filter(PlanLimit.plan_id == plan.id).all():
        limits[pl.limit_code] = pl.value

    return PlanSummary(
        id=plan.id,
        code=plan.code,
        name=plan.name,
        price=plan.price,
        currency_code=currency.code if currency else "USD",
        interval=plan.interval,
        trial_days=plan.trial_days,
        features=features,
        limits=limits,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/plans", response_model=list[PlanSummary])
def list_available_plans(db: Session = Depends(get_db)):
    """Lista los planes disponibles (público, sin auth).

    Solo devuelve planes activos.
    """
    plans = db.query(Plan).filter(Plan.is_active.is_(True)).order_by(Plan.price).all()
    return [_plan_to_summary(db, p) for p in plans]


@router.get("/current", response_model=SubscriptionInfo)
def get_current_subscription(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Obtiene la suscripción actual del tenant."""
    plan = None
    if current_tenant.plan_id:
        plan = db.query(Plan).filter(Plan.id == current_tenant.plan_id).first()

    days_remaining = None
    if current_tenant.trial_ends_at:
        delta = current_tenant.trial_ends_at - datetime.now(timezone.utc)
        days_remaining = max(0, delta.days)

    return SubscriptionInfo(
        plan_id=current_tenant.plan_id,
        plan_name=plan.name if plan else None,
        status=current_tenant.subscription_status,
        trial_ends_at=current_tenant.trial_ends_at,
        days_remaining=days_remaining,
    )


@router.post("/select-plan", response_model=SelectPlanResponse)
def select_plan(
    data: SelectPlanRequest,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Selecciona un plan para el tenant actual.

    Si el plan tiene trial_days > 0, activa el trial.
    """
    plan = db.query(Plan).filter(Plan.id == data.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan no encontrado",
        )

    if not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan no disponible",
        )

    # Actualizar tenant
    current_tenant.plan_id = plan.id

    if plan.trial_days > 0:
        current_tenant.trial_ends_at = datetime.now(timezone.utc) + timedelta(
            days=plan.trial_days
        )
        current_tenant.subscription_status = "trial"
        msg = f"Plan {plan.name} activado. Tienes {plan.trial_days} días de prueba."
    else:
        current_tenant.trial_ends_at = None
        current_tenant.subscription_status = "activo"
        msg = f"Plan {plan.name} activado."

    db.flush()

    return SelectPlanResponse(
        plan_id=plan.id,
        plan_name=plan.name,
        status=current_tenant.subscription_status,
        trial_ends_at=current_tenant.trial_ends_at,
        message=msg,
    )