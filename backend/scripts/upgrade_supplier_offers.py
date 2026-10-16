"""Actualiza la tabla supplier_resources en todos los tenants."""

from sqlalchemy import text

from app.core.database import SessionLocal
from app.models import Tenant


def upgrade() -> None:
    db = SessionLocal()
    try:
        # 1. Public
        print("=" * 60)
        print("Actualizando public.supplier_resources...")
        statements = [
            "ALTER TABLE public.supplier_resources ADD COLUMN IF NOT EXISTS unit_price NUMERIC(12, 4)",
            "ALTER TABLE public.supplier_resources ADD COLUMN IF NOT EXISTS currency_id UUID",
            "ALTER TABLE public.supplier_resources ADD COLUMN IF NOT EXISTS lead_time_days INTEGER",
            "ALTER TABLE public.supplier_resources ADD COLUMN IF NOT EXISTS min_quantity NUMERIC(14, 4)",
            "ALTER TABLE public.supplier_resources ADD COLUMN IF NOT EXISTS valid_until TIMESTAMPTZ",
        ]
        for stmt in statements:
            db.execute(text(stmt))
        db.commit()
        print("  ✓ public actualizado")

        # 2. Tenants
        tenants = db.query(Tenant).all()
        print(f"\nEncontrados {len(tenants)} tenants")
        for tenant in tenants:
            schema = tenant.schema_name
            print(f"\nActualizando {tenant.name} ({schema})...")
            tenant_statements = [
                f'ALTER TABLE "{schema}".supplier_resources ADD COLUMN IF NOT EXISTS unit_price NUMERIC(12, 4)',
                f'ALTER TABLE "{schema}".supplier_resources ADD COLUMN IF NOT EXISTS currency_id UUID',
                f'ALTER TABLE "{schema}".supplier_resources ADD COLUMN IF NOT EXISTS lead_time_days INTEGER',
                f'ALTER TABLE "{schema}".supplier_resources ADD COLUMN IF NOT EXISTS min_quantity NUMERIC(14, 4)',
                f'ALTER TABLE "{schema}".supplier_resources ADD COLUMN IF NOT EXISTS valid_until TIMESTAMPTZ',
            ]
            for stmt in tenant_statements:
                try:
                    db.execute(text(stmt))
                except Exception as e:
                    print(f"  ⚠️  Error: {e}")
                    db.rollback()
                    continue
            db.commit()
            print(f"  ✓ {schema} listo")

        print(f"\n{'=' * 60}")
        print(f"✅ {len(tenants) + 1} schemas procesados")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Iniciando migración de supplier_resources...")
    upgrade()
    print("Migración completada")