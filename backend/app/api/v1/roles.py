from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Permission, Role, RolePermission
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_role_or_404(db: Session, role_id: UUID) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )
    return role


def _validate_permission_ids(db: Session, permission_ids: list[UUID]) -> None:
    """Verifica que todos los permission_ids existen."""
    if not permission_ids:
        return
    found = (
        db.query(Permission.id)
        .filter(Permission.id.in_(permission_ids))
        .all()
    )
    found_ids = {row.id for row in found}
    missing = set(permission_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permisos no encontrados: {sorted(str(m) for m in missing)}",
        )


def _replace_permissions(
    db: Session, role_id: UUID, permission_ids: list[UUID]
) -> None:
    """Reemplaza los permisos de un rol."""
    db.query(RolePermission).filter(
        RolePermission.role_id == role_id
    ).delete()
    for perm_id in permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=perm_id))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    """Lista todos los roles del sistema (globales)."""
    roles = db.query(Role).order_by(Role.name).all()
    return [RoleResponse.model_validate(r) for r in roles]


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(role_id: UUID, db: Session = Depends(get_db)):
    """Obtiene un rol por ID."""
    return RoleResponse.model_validate(_get_role_or_404(db, role_id))


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(data: RoleCreate, db: Session = Depends(get_db)):
    """Crea un nuevo rol global.

    Solo el sistema debe crear roles con is_system=True.
    Los roles de usuario se crean con is_system=False.
    """
    existing = db.query(Role).filter(Role.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un rol con ese nombre",
        )

    _validate_permission_ids(db, data.permission_ids)

    role = Role(
        name=data.name,
        description=data.description,
        is_system=data.is_system,
    )
    db.add(role)
    db.flush()

    _replace_permissions(db, role.id, data.permission_ids)

    db.commit()
    db.refresh(role)
    return RoleResponse.model_validate(role)


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    data: RoleUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza un rol. Los roles del sistema (is_system=True) no se renombran."""
    role = _get_role_or_404(db, role_id)

    update_data = data.model_dump(exclude_unset=True, exclude={"permission_ids"})

    # Un rol del sistema no puede renombrarse ni desmarcarse como sistema
    if role.is_system:
        update_data.pop("name", None)
        update_data.pop("is_system", None)

    for key, value in update_data.items():
        setattr(role, key, value)

    if data.permission_ids is not None:
        _validate_permission_ids(db, data.permission_ids)
        _replace_permissions(db, role.id, data.permission_ids)

    db.commit()
    db.refresh(role)
    return RoleResponse.model_validate(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: UUID, db: Session = Depends(get_db)):
    """Elimina un rol. Los roles del sistema no se pueden eliminar."""
    role = _get_role_or_404(db, role_id)

    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede eliminar un rol del sistema",
        )

    # Borrar relaciones primero
    db.query(RolePermission).filter(
        RolePermission.role_id == role_id
    ).delete()

    db.delete(role)
    db.commit()