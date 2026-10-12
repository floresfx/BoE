from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User, Vertical
from app.schemas.vertical import VerticalCreate, VerticalResponse, VerticalUpdate

router = APIRouter(prefix="/verticals", tags=["verticals"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_vertical_or_404(db: Session, vertical_id: UUID) -> Vertical:
    vertical = db.query(Vertical).filter(Vertical.id == vertical_id).first()
    if not vertical:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vertical no encontrado",
        )
    return vertical


# ---------------------------------------------------------------------------
# Endpoints (GET públicos, POST/PUT autenticados)
# ---------------------------------------------------------------------------

@router.get("", response_model=list[VerticalResponse])
def list_verticals(db: Session = Depends(get_db)):
    """Lista todos los verticales. Público (para signup)."""
    return [VerticalResponse.model_validate(v) for v in db.query(Vertical).all()]


@router.get("/{vertical_id}", response_model=VerticalResponse)
def get_vertical(vertical_id: UUID, db: Session = Depends(get_db)):
    """Obtiene un vertical por ID. Público."""
    return VerticalResponse.model_validate(_get_vertical_or_404(db, vertical_id))


@router.post("", response_model=VerticalResponse, status_code=status.HTTP_201_CREATED)
def create_vertical(
    data: VerticalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un nuevo vertical. Requiere autenticación."""
    existing = db.query(Vertical).filter(Vertical.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un vertical con ese nombre",
        )

    vertical = Vertical(**data.model_dump())
    db.add(vertical)
    db.commit()
    db.refresh(vertical)
    return VerticalResponse.model_validate(vertical)


@router.put("/{vertical_id}", response_model=VerticalResponse)
def update_vertical(
    vertical_id: UUID,
    data: VerticalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un vertical. Requiere autenticación."""
    vertical = _get_vertical_or_404(db, vertical_id)

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != vertical.name:
        existing = (
            db.query(Vertical).filter(Vertical.name == update_data["name"]).first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un vertical con ese nombre",
            )

    for key, value in update_data.items():
        setattr(vertical, key, value)

    db.commit()
    db.refresh(vertical)
    return VerticalResponse.model_validate(vertical)