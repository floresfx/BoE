from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import AccessLog, User
from app.schemas.access_log import AccessLogResponse

router = APIRouter(prefix="/access-logs", tags=["access-logs"])


@router.get("", response_model=list[AccessLogResponse])
def list_access_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los logs de acceso del usuario actual."""
    logs = (
        db.query(AccessLog)
        .filter(AccessLog.user_id == current_user.id)
        .order_by(AccessLog.created_at.desc())
        .all()
    )
    return [AccessLogResponse.model_validate(log) for log in logs]