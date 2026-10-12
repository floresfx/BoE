from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Profile, User
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_profile_or_404(db: Session, profile_id: UUID) -> Profile:
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado",
        )
    return profile


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ProfileResponse])
def list_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos los perfiles."""
    return [ProfileResponse.model_validate(p) for p in db.query(Profile).all()]


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene un perfil por ID."""
    return ProfileResponse.model_validate(_get_profile_or_404(db, profile_id))


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un nuevo perfil."""
    existing = db.query(Profile).filter(Profile.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un perfil con ese nombre",
        )

    profile = Profile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return ProfileResponse.model_validate(profile)


@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: UUID,
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un perfil."""
    profile = _get_profile_or_404(db, profile_id)

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != profile.name:
        existing = (
            db.query(Profile).filter(Profile.name == update_data["name"]).first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un perfil con ese nombre",
            )

    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return ProfileResponse.model_validate(profile)