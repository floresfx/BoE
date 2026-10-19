"""Helper para migraciones multi-tenant.

Uso:
    python -m scripts.migrate_tenant add_column_inventory_costing_method
    python -m scripts.migrate_tenant create_production_tables
"""

import sys
from sqlalchemy import text

from app.core.database import SessionLocal
from app.models import Tenant


MIGRATIONS = {
    "add_column_inventory_costing_method": """
        ALTER TABLE {schema}.tenants
        ADD COLUMN IF NOT EXISTS inventory_costing_method VARCHAR(20)
        NOT NULL DEFAULT 'fifo';
    """,
    "add_column_quantity_received": """
        ALTER TABLE {schema}.purchase_request_lines
        ADD COLUMN IF NOT EXISTS quantity_received NUMERIC(14, 4)
        NOT NULL DEFAULT 0;
    """,
    "create_production_tables": """
        CREATE TABLE IF NOT EXISTS {schema}.production_plans (
            id UUID PRIMARY KEY,
            code VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'draft',
            target_date TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (code)
        );
        CREATE INDEX IF NOT EXISTS ix_pp_status ON {schema}.production_plans (status);
        CREATE INDEX IF NOT EXISTS ix_pp_target_date ON {schema}.production_plans (target_date);

        CREATE TABLE IF NOT EXISTS {schema}.production_orders (
            id UUID PRIMARY KEY,
            code VARCHAR(50) NOT NULL,
            plan_id UUID REFERENCES {schema}.production_plans(id) ON DELETE SET NULL,
            bundle_id UUID NOT NULL REFERENCES {schema}.bundles(id) ON DELETE RESTRICT,
            quantity NUMERIC(14, 4) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'draft',
            start_date TIMESTAMPTZ,
            end_date TIMESTAMPTZ,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (code)
        );
        CREATE INDEX IF NOT EXISTS ix_po_status ON {schema}.production_orders (status);
        CREATE INDEX IF NOT EXISTS ix_po_bundle ON {schema}.production_orders (bundle_id);
    """,
}


def run_migration(migration_name: str) -> None:
    """Ejecuta una migración en todos los tenants."""
    if migration_name not in MIGRATIONS:
        print(f"❌ Migración no encontrada: {migration_name}")
        print(f"   Disponibles: {', '.join(MIGRATIONS.keys())}")
        sys.exit(1)

    sql_template = MIGRATIONS[migration_name]
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for tenant in tenants:
            schema = tenant.schema_name
            print(f"Migrando {tenant.name} ({schema})...")
            sql = sql_template.format(schema=f'"{schema}"')
            db.execute(text(sql))
            db.commit()
            print(f"  ✓ {schema} listo")
        print(f"\n✅ {len(tenants)} tenants migrados con '{migration_name}'")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m scripts.migrate_tenant <migration_name>")
        print(f"Disponibles: {', '.join(MIGRATIONS.keys())}")
        sys.exit(1)
    run_migration(sys.argv[1])