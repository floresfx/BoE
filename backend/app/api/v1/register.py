"""Endpoint de registro self-service.

Permite a un usuario anónimo crear un tenant + admin user
en una sola transacción atómica.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.models import (
    Country,
    Currency,
    Role,
    Tenant,
    User,
    UserRole,
    Vertical,
)
from app.schemas.register import RegisterRequest, RegisterResponse
from app.services.tenant_service import create_tenant_with_schema

router = APIRouter(prefix="/register", tags=["register"])


@router.post(
    "",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuevo tenant + admin user.

    Pasos:
    1. Validar que el email no exista.
    2. Validar que el tax_id no exista.
    3. Validar que el vertical exista.
    4. Validar que el país exista.
    5. Crear el tenant + su schema.
    6. Crear el admin user.
    7. Asignar el rol Admin al user.
    8. Devolver tenant + user.
    """

    # 1. Validar email único
    existing_email = (
        db.query(User).filter(User.email == data.admin_email).first()
    )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email",
        )

    # 2. Validar tax_id único
    existing_tax = (
        db.query(Tenant).filter(Tenant.tax_id == data.tax_id).first()
    )
    if existing_tax:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un tenant con ese tax_id",
        )

    # 3. Validar vertical
    vertical = (
        db.query(Vertical).filter(Vertical.id == data.vertical_id).first()
    )
    if not vertical:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vertical no encontrado",
        )

    # 4. Validar país
    country = (
        db.query(Country).filter(Country.code == data.country_code).first()
    )
    if not country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="País no encontrado",
        )

    # 5. Crear el tenant
    tenant = Tenant(
        name=data.company_name,
        tax_id=data.tax_id,
        tax_id_type=data.tax_id_type,
        admin_email=data.admin_email,
        vertical_id=data.vertical_id,
        timezone=country.timezone.code if country.timezone else "UTC",
        country=country.name,
        province="",
        city="",
        status="activo",
    )
    tenant = create_tenant_with_schema(db, tenant)

    # 6. Crear el admin user
    user = User(
        tenant_id=tenant.id,
        email=data.admin_email,
        password_hash=hash_password(data.admin_password),
        first_name=data.admin_first_name,
        last_name=data.admin_last_name,
        phone=data.admin_phone,
        phone_verified=False,
        status="activo",
    )
    db.add(user)
    db.flush()

    # 7. Asignar el rol Admin
    admin_role = (
        db.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )                                                                                                   
    if admin_role:
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        db.flush()

    return RegisterResponse(
        tenant_id=tenant.id,
        user_id=user.id,
        email=user.email,
        schema_name=tenant.schema_name,
        message=(
            "Registro exitoso. "
            "Inicia sesión con tu email y contraseña para continuar."
        ),
    )