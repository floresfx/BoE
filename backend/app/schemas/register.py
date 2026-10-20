"""Schemas para el registro self-service.

Un usuario anónimo se registra, crea un tenant y un admin user
en una sola transacción atómica.
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema


class RegisterRequest(BaseModel):
    """Datos para registrarse (crear tenant + admin user)."""

    # Datos del tenant
    company_name: str = Field(..., min_length=1, max_length=100)
    tax_id: str = Field(..., min_length=1, max_length=50)
    tax_id_type: str = Field(default="RIF", max_length=20)
    vertical_id: UUID
    country_code: str = Field(..., min_length=2, max_length=2)


    # Datos del admin user
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8, max_length=100)
    admin_first_name: str = Field(..., min_length=1, max_length=100)
    admin_last_name: str = Field(..., min_length=1, max_length=100)
    admin_phone: str = Field(..., min_length=5, max_length=20)


class RegisterResponse(BaseSchema):
    """Respuesta del registro."""

    tenant_id: UUID
    user_id: UUID
    email: str
    schema_name: str
    message: str