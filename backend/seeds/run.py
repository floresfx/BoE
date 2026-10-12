"""Script para ejecutar los datos semilla."""

from app.core.database import SessionLocal
from seeds.admin import seed_admin
from seeds.permissions import seed_permissions
from seeds.plans import seed_plans
from seeds.profiles import seed_profiles
from seeds.roles import seed_roles  # ← ver nota abajo
from seeds.verticals import seed_verticals


def run_seeds() -> None:
    """Ejecuta todos los seeds en orden de dependencias."""
    db = SessionLocal()
    try:
        print("🌱 Iniciando seeds...")

        v = seed_verticals(db)
        print(f"   ✅ Verticales: {v} creados")

        p = seed_plans(db)
        print(f"   ✅ Planes: {p} creados")

        pr = seed_profiles(db)
        print(f"   ✅ Perfiles: {pr} creados")

        pe = seed_permissions(db)
        print(f"   ✅ Permisos: {pe} creados")

        r = seed_roles(db)
        print(f"   ✅ Roles: {r} creados")

        a = seed_admin(db)
        print(f"   ✅ Admin: {a}")

        print("🌱 Seeds completados")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seeds()