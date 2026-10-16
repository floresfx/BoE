"""Crea las tablas de supplier en todos los tenants existentes.

Uso:
    python -m scripts.init_supplier_tables
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
                CREATE TABLE IF NOT EXISTS "{schema}"."suppliers" (
                    id UUID PRIMARY KEY,
                    code VARCHAR(30) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    tax_id VARCHAR(50),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    address TEXT,
                    contact_name VARCHAR(200),
                    notes TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (code)
                )
            """))

            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."supplier_resources" (
                    id UUID PRIMARY KEY,
                    supplier_id UUID NOT NULL REFERENCES "{schema}".suppliers(id) ON DELETE CASCADE,
                    resource_id UUID NOT NULL REFERENCES "{schema}".resources(id) ON DELETE CASCADE,
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (supplier_id, resource_id)
                )
            """))

            db.commit()
            print(f"  ✓ {schema} listo")

        print(f"\n✅ {len(tenants)} tenants procesados")
    finally:
        db.close()


if __name__ == "__main__":
    init_tables()