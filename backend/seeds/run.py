"""Script para ejecutar los datos semilla."""

from app.core.database import SessionLocal
from seeds.admin import seed_admin
from seeds.catalogs import (
    seed_attribute_types,
    seed_attributes,
    seed_categories,
    seed_currencies,
    seed_date_formats,
    seed_number_formats,
    seed_subcategories,
    seed_timezones,
    seed_unit_categories,
    seed_unit_conversions,
    seed_units,
    seed_verticals_attributes,
)
from seeds.permissions import seed_permissions
from seeds.plans import seed_plans
from seeds.profiles import seed_profiles
from seeds.roles import seed_roles
from seeds.verticals import seed_verticals


def run_seeds() -> None:
    """Ejecuta todos los seeds en orden de dependencias."""
    db = SessionLocal()
    try:
        print("🌱 Iniciando seeds...")

        # =====================================================================
        # BLOQUE 1 — Catálogos simples (sin dependencias)
        # =====================================================================
        print("\n🌍 Catálogos simples")

        c = seed_currencies(db)
        print(f"   ✅ Monedas: {c} creadas")

        tz = seed_timezones(db)
        print(f"   ✅ Zonas horarias: {tz} creadas")

        df = seed_date_formats(db)
        print(f"   ✅ Formatos de fecha: {df} creados")

        nf = seed_number_formats(db)
        print(f"   ✅ Formatos de número: {nf} creados")

        at = seed_attribute_types(db)
        print(f"   ✅ Tipos de atributo: {at} creados")

        # =====================================================================
        # BLOQUE 2 — Catálogos dependientes
        # =====================================================================
        print("\n📚 Catálogos dependientes")

        uc = seed_unit_categories(db)
        print(f"   ✅ Categorías de unidades: {uc} creadas")

        u = seed_units(db)
        print(f"   ✅ Unidades: {u} creadas")

        uconv = seed_unit_conversions(db)
        print(f"   ✅ Conversiones: {uconv} creadas")

        cat = seed_categories(db)
        print(f"   ✅ Categorías: {cat} creadas")

        sub = seed_subcategories(db)
        print(f"   ✅ Subcategorías: {sub} creadas")

        attrs = seed_attributes(db)
        print(f"   ✅ Atributos: {attrs} creados")

        # =====================================================================
        # Catálogos existentes
        # =====================================================================
        print("\n📚 Catálogos existentes")

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

        # =====================================================================
        # Relaciones N:M (dependen de verticales + attributes)
        # =====================================================================
        print("\n🔗 Relaciones")

        va = seed_verticals_attributes(db)
        print(f"   ✅ Atributos por vertical: {va} creados")

        # =====================================================================
        # Admin (al final)
        # =====================================================================
        print("\n👤 Admin")
        seed_admin(db)

        print("\n🌱 Seeds completados")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seeds()