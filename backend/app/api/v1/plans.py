from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Plan, User
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate

router = APIRouter(prefix="/plans", tags=["plans"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_plan_or_404(db: Session, plan_id: UUID) -> Plan:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan no encontrado",
        )
    return plan


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[PlanResponse])
def list_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos los planes."""
    return [PlanResponse.model_validate(p) for p in db.query(Plan).all()]


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene un plan por ID."""
    return PlanResponse.model_validate(_get_plan_or_404(db, plan_id))


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    data: PlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un nuevo plan."""
    existing = db.query(Plan).filter(Plan.code == data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un plan con ese code",
        )

    plan = Plan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PlanResponse.model_validate(plan)


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: UUID,
    data: PlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un plan. `code` no es editable."""
    plan = _get_plan_or_404(db, plan_id)

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    return PlanResponse.model_validate(plan)