"""Crea las tablas de inventory en todos los tenants existentes.

Uso:
    python -m scripts.init_inventory_tables
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

            # Warehouses
            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."warehouses" (
                    id UUID PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    code VARCHAR(20) NOT NULL,
                    address TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (code)
                )
            """))

            # Stock lots
            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."stock_lots" (
                    id UUID PRIMARY KEY,
                    warehouse_id UUID NOT NULL REFERENCES "{schema}".warehouses(id),
                    resource_id UUID NOT NULL REFERENCES "{schema}".resources(id),
                    lot_code VARCHAR(50) NOT NULL,
                    quantity NUMERIC(14, 4) NOT NULL DEFAULT 0,
                    expiration TIMESTAMPTZ,
                    unit_cost NUMERIC(12, 4),
                    received_at TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (warehouse_id, resource_id, lot_code)
                )
            """))

            # Movements
            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."movements" (
                    id UUID PRIMARY KEY,
                    warehouse_id UUID NOT NULL REFERENCES "{schema}".warehouses(id),
                    resource_id UUID NOT NULL REFERENCES "{schema}".resources(id),
                    lot_id UUID REFERENCES "{schema}".stock_lots(id),
                    movement_type VARCHAR(20) NOT NULL,
                    quantity NUMERIC(14, 4) NOT NULL,
                    unit_cost NUMERIC(12, 4),
                    reference VARCHAR(100),
                    notes TEXT,
                    created_by UUID,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """))
            db.commit()
            print(f"  ✓ {schema} listo")

        print(f"\n✅ {len(tenants)} tenants procesados")
    finally:
        db.close()


if __name__ == "__main__":
    init_tables()