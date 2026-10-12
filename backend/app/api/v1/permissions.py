from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Permission, User
from app.schemas.permission import PermissionResponse

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("", response_model=list[PermissionResponse])
def list_permissions(
    module: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los permisos del sistema.

    Solo lectura: los permisos los crea el seed, no la API.
    """
    query = db.query(Permission)
    if module:
        query = query.filter(Permission.module == module)
    return [PermissionResponse.model_validate(p) for p in query.all()]