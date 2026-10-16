"""Crea las tablas de bundle en todos los tenants existentes.

Uso:
    python -m scripts.init_bundle_tables
"""

from sqlalchemy import text

from app.core.database import SessionLocal
from app.models import Tenant


def init_tables() -> None:
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for tenant in tenants:
            schema = tenant.schema_name
            print(f"Procesando {tenant.name} ({schema})...")

            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."bundles" (
                    id UUID PRIMARY KEY,
                    code VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    category_id UUID,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (code)
                )
            """))

            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."bundle_components" (
                    id UUID PRIMARY KEY,
                    bundle_id UUID NOT NULL REFERENCES "{schema}".bundles(id) ON DELETE CASCADE,
                    resource_id UUID NOT NULL REFERENCES "{schema}".resources(id) ON DELETE CASCADE,
                    quantity NUMERIC(14, 4) NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (bundle_id, resource_id)
                )
            """))

            db.commit()
            print(f"  ✓ {schema} listo")

        print(f"\n✅ {len(tenants)} tenants procesados")
    finally:
        db.close()


if __name__ == "__main__":
    init_tables()