from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import SecureDevice, User
from app.schemas.secure_device import SecureDeviceCreate, SecureDeviceResponse

router = APIRouter(prefix="/secure-devices", tags=["secure-devices"])


@router.get("", response_model=list[SecureDeviceResponse])
def list_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los dispositivos seguros del usuario."""
    devices = (
        db.query(SecureDevice)
        .filter(SecureDevice.user_id == current_user.id)
        .all()
    )
    return [SecureDeviceResponse.model_validate(d) for d in devices]


@router.post("", response_model=SecureDeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    data: SecureDeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra un nuevo dispositivo seguro. Máximo 2."""
    count = (
        db.query(SecureDevice)
        .filter(SecureDevice.user_id == current_user.id)
        .count()
    )
    if count >= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 2 dispositivos seguros por usuario",
        )

    device = SecureDevice(
        user_id=current_user.id,
        fingerprint=data.fingerprint,
        ip=data.ip,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return SecureDeviceResponse.model_validate(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un dispositivo seguro."""
    device = (
        db.query(SecureDevice)
        .filter(SecureDevice.id == device_id, SecureDevice.user_id == current_user.id)
        .first()
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )
    db.delete(device)
    db.commit()