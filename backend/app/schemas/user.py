from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema

UserStatus = Literal["activo", "inactivo", "suspendido"]


class UserBase(BaseModel):
    """Campos base del usuario."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=50)


class UserCreate(UserBase):
    """Schema para crear un usuario.

    El tenant_id se toma del token del usuario autenticado.
    NO se acepta desde el body (evita escalada de privilegios).
    """
    password: str = Field(..., min_length=8, max_length=100)
    phone_verified: bool = False
    status: UserStatus = "activo"
    # tenant_id NO se expone


class UserUpdate(BaseModel):
    """Schema para actualizar un usuario."""
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    phone_verified: bool | None = None
    status: UserStatus | None = None


class UserResponse(UserBase):
    """Schema de respuesta del usuario."""
    id: UUID
    tenant_id: UUID
    phone_verified: bool
    status: UserStatus
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class UserListResponse(BaseSchema):
    """Lista de usuarios."""
    items: list[UserResponse]
    total: int


class UserLogin(BaseModel):
    """Schema para login."""
    email: EmailStr
    password: str


class UserLoginResponse(BaseSchema):
    """Respuesta del login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse