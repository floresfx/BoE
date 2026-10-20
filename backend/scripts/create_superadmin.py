"""Crea un tenant + user con rol SuperAdmin para administrar el SaaS.

Uso:
    python -m scripts.create_superadmin

Crea:
- Un tenant especial llamado "SaaS Admin" (o reutiliza si existe).
- Un user SuperAdmin con email/contraseña definidos aquí.
- Asigna el rol SuperAdmin al user.

⚠️ Cambia el EMAIL y PASSWORD antes de correrlo.
"""

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Role, Tenant, User, UserRole, Vertical
from app.services.tenant_service import create_tenant_with_schema

# ⚠️ CAMBIA ESTOS VALORES ANTES DE CORRERLO
SUPERADMIN_EMAIL = "superadmin@boempr.com"
SUPERADMIN_PASSWORD = "CambiarEstoYa123!"
SUPERADMIN_FIRST_NAME = "Super"
SUPERADMIN_LAST_NAME = "Admin"
SUPERADMIN_COMPANY_NAME = "SaaS Admin"
SUPERADMIN_TAX_ID = "SAAS-00000001"


def create_superadmin() -> None:
    db = SessionLocal()
    try:
        # 1. Verificar si ya existe
        existing = db.query(User).filter(User.email == SUPERADMIN_EMAIL).first()
        if existing:
            print(f"SuperAdmin ya existe: {SUPERADMIN_EMAIL}")
            return

        # 2. Buscar o crear tenant "SaaS Admin"
        tenant = db.query(Tenant).filter(Tenant.tax_id == SUPERADMIN_TAX_ID).first()
        if not tenant:
            # Usar el primer vertical disponible
            vertical = db.query(Vertical).first()
            if not vertical:
                raise RuntimeError(
                    "No hay verticales. Corre `python -m seeds.run` primero."
                )

            tenant = Tenant(
                name=SUPERADMIN_COMPANY_NAME,
                tax_id=SUPERADMIN_TAX_ID,
                tax_id_type="OTRO",
                admin_email=SUPERADMIN_EMAIL,
                vertical_id=vertical.id,
                timezone="America/Caracas",
                country="Venezuela",
                schema_name="",  # se asigna en create_tenant_with_schema
                status="activo",
            )
            tenant = create_tenant_with_schema(db, tenant)
            print(f"Tenant creado: {tenant.name} ({tenant.schema_name})")

        # 3. Crear user
        user = User(
            tenant_id=tenant.id,
            email=SUPERADMIN_EMAIL,
            password_hash=hash_password(SUPERADMIN_PASSWORD),
            first_name=SUPERADMIN_FIRST_NAME,
            last_name=SUPERADMIN_LAST_NAME,
            phone="0000000000",
            phone_verified=True,
            status="activo",
        )
        db.add(user)
        db.flush()

        # 4. Asignar rol SuperAdmin
        role = db.query(Role).filter(Role.name == "SuperAdmin").first()
        if not role:
            raise RuntimeError(
                "Rol SuperAdmin no existe. Corre `python -m seeds.run` primero."
            )
        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.commit()

        print(f"✅ SuperAdmin creado: {SUPERADMIN_EMAIL}")
        print(f"   Contraseña: {SUPERADMIN_PASSWORD}")
        print(f"   Tenant: {tenant.name}")
    finally:
        db.close()


if __name__ == "__main__":
    create_superadmin()