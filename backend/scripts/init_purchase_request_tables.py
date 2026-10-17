"""Crea las tablas de purchase requests en todos los tenants existentes.

Uso:
    python -m scripts.init_purchase_request_tables
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
                CREATE TABLE IF NOT EXISTS "{schema}"."purchase_requests" (
                    id UUID PRIMARY KEY,
                    code VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'draft',
                    needed_by TIMESTAMPTZ,
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (code)
                )
            """))

            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."purchase_request_lines" (
                    id UUID PRIMARY KEY,
                    request_id UUID NOT NULL REFERENCES "{schema}".purchase_requests(id) ON DELETE CASCADE,
                    resource_id UUID NOT NULL REFERENCES "{schema}".resources(id),
                    quantity NUMERIC(14, 4) NOT NULL,
                    supplier_id UUID REFERENCES "{schema}".suppliers(id) ON DELETE SET NULL,
                    notes TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (request_id, resource_id)
                )
            """))

            db.commit()
            print(f"  ✓ {schema} listo")

        print(f"\n✅ {len(tenants)} tenants procesados")
    finally:
        db.close()


if __name__ == "__main__":
    init_tables()