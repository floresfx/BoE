from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import Tenant, User

security = HTTPBearer()

_SCHEMA_CHARS_OK = set("abcdefghijklmnopqrstuvwxyz0123456789_")


def _is_safe_schema(schema: str) -> bool:
    return bool(schema) and all(c in _SCHEMA_CHARS_OK for c in schema.lower())


def _user_status_error(user_status: str) -> HTTPException:
    detail = {
        "inactivo": "Usuario inactivo",
        "suspendido": "Usuario suspendido",
    }.get(user_status, "Usuario no activo")
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Obtiene el usuario actual desde el token JWT."""
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    if user.status != "activo":
        raise _user_status_error(user.status)

    return user


def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tenant:
    """Obtiene el tenant y aplica SET LOCAL search_path en la sesión."""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado",
        )

    if tenant.status != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant no activo",
        )

    schema = tenant.schema_name
    if not _is_safe_schema(schema):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Schema inválido",
        )

    db.execute(text(f'SET LOCAL search_path TO "{schema}", public'))
    return tenant