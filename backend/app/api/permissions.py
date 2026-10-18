"""Dependencia require_permission para RBAC."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import (
    Permission,
    RolePermission,
    User,
    UserRole,
)


def require_permission(module: str, action: str):
    """Factory de dependencia que verifica un permiso concreto."""

    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        user_perms = (
            db.query(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .filter(UserRole.user_id == current_user.id)
            .all()
        )

        if not any(p.module == module and p.action == action for p in user_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {module}:{action}",
            )
        return current_user

    return checker