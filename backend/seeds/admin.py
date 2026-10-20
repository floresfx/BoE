"""Seed del tenant + admin inicial.

Crea:
1. Un tenant de prueba con su schema real (CREATE SCHEMA).
2. Un usuario admin asignado al rol "Admin" (global).
"""

from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Role, Tenant, User, UserRole

# IDs/valores del seed (idempotente por tax_id)
ADMIN_TAX_ID = "J-00000000-0"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"
ADMIN_TENANT_NAME = "Tenant de Prueba"


def _generate_schema_name() -> str:
    """Mismo formato que create_tenant en la API."""
    return f"tenant_{uuid4().hex}"


def seed_admin(db: Session) -> None:
    """Crea el tenant de prueba y su admin. Idempotente."""
    # 1. ¿Ya existe el tenant?
    existing = db.query(Tenant).filter(Tenant.tax_id == ADMIN_TAX_ID).first()
    if existing:
        print("   ⚠️  Admin ya existe")
        return

    # 2. Crear tenant con schema generado
    schema_name = _generate_schema_name()
    tenant = Tenant(
        name=ADMIN_TENANT_NAME,
        tax_id=ADMIN_TAX_ID,
        tax_id_type="RIF",
        admin_email=ADMIN_EMAIL,
        timezone="America/Caracas",
        country="Venezuela",
        province="Miranda",
        city="Caracas",
        schema_name=schema_name,
        status="activo",
    )
    db.add(tenant)
    db.flush()  # asigna id sin commit

    # 3. Crear el schema real en Postgres
    db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    # 4. Crear usuario admin
    user = User(
        tenant_id=tenant.id,
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        first_name="Admin",
        last_name="Test",
        phone="04141234567",
        phone_verified=True,
        status="activo",
    )
    db.add(user)
    db.flush()

    # 5. Asignar rol "Admin" (global, creado por seed_roles)
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if admin_role is None:
        raise RuntimeError(
            "Rol 'Admin' no existe. Ejecuta seed_roles() antes que seed_admin()."
        )

    db.add(UserRole(user_id=user.id, role_id=admin_role.id))

    db.commit()
    print(f"   ✅ Admin creado: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")