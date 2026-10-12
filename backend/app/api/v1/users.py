from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.core.security import hash_password
from app.models import Tenant, User
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_user_in_tenant_or_404(
    db: Session, user_id: UUID, tenant_id: UUID
) -> User:
    """Busca un user por id Y tenant. Evita fugas entre tenants."""
    user = (
        db.query(User)
        .filter(User.id == user_id, User.tenant_id == tenant_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=UserListResponse)
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lista los usuarios del tenant autenticado.

    El filtro por tenant es obligatorio y viene del token, no del cliente.
    """
    query = db.query(User).filter(User.tenant_id == current_tenant.id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in items],
        total=total,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Obtiene un usuario del tenant autenticado."""
    user = _get_user_in_tenant_or_404(db, user_id, current_tenant.id)
    return UserResponse.model_validate(user)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Crea un usuario en el tenant autenticado.

    El tenant_id NUNCA viene del body: se toma del token.
    Esto evita que un usuario cree users en otros tenants.
    """
    # Email único global
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email",
        )

    user = User(
        tenant_id=current_tenant.id,          # ← del token, no del body
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        phone_verified=data.phone_verified,
        status=data.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza un usuario del tenant autenticado."""
    user = _get_user_in_tenant_or_404(db, user_id, current_tenant.id)

    update_data = data.model_dump(exclude_unset=True)

    # Si cambia el email, verificar unicidad global
    if "email" in update_data and update_data["email"] != user.email:
        existing = (
            db.query(User)
            .filter(User.email == update_data["email"], User.id != user.id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese email",
            )

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)