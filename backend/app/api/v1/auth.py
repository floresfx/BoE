from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.user import UserLogin, UserLoginResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _status_error(user_status: str) -> HTTPException:
    detail = {
        "inactivo": "Usuario inactivo",
        "suspendido": "Usuario suspendido",
    }.get(user_status, "Usuario no activo")
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


@router.post("/login", response_model=UserLoginResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """Inicia sesión con email y password.

    Email es único global. Un usuario pertenece a un solo tenant.
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if user.status != "activo":
        raise _status_error(user.status)

    # Actualizar último login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=str(user.id))

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Obtiene el usuario actual."""
    return UserResponse.model_validate(current_user)