"""Aplica TODAS las migraciones de Alembic a todos los tenants existentes.

Este script reemplaza todos los scripts init_*.py y migrate_tenant*.py.
Se ejecuta después de `alembic upgrade head` (que migra el schema public).

Uso:
    python -m scripts.migrate_all_tenants

Es idempotente: se puede ejecutar múltiples veces sin efectos adversos.
"""

import re
from pathlib import Path

from sqlalchemy import text

from app.core.database import SessionLocal
from app.models import Tenant


# Directorio de migraciones de Alembic
ALEMBIC_VERSIONS_DIR = Path(__file__).parent.parent / "alembic" / "versions"


def _read_alembic_migrations() -> list[tuple[str, str]]:
    """Lee todos los archivos de migración y extrae el SQL de cada uno.

    Retorna una lista de (revision_id, sql_content).
    """
    migrations = []
    for file in sorted(ALEMBIC_VERSIONS_DIR.glob("*.py")):
        content = file.read_text(encoding="utf-8")
        # Extraer el revision_id del archivo
        match = re.search(r'revision\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            continue
        revision_id = match.group(1)
        migrations.append((revision_id, content))
    return migrations


# Migraciones SQL que se aplican a cada tenant.
# Cada entrada es (descripción, SQL con {schema} como placeholder).
TENANT_MIGRATIONS = [
    # --- Resources ---
    (
        "resources: waste_percent",
        """
        ALTER TABLE "{schema}"."resources"
        ADD COLUMN IF NOT EXISTS waste_percent NUMERIC(5, 2) NOT NULL DEFAULT 0;
        """,
    ),
    # --- Bundles ---
    (
        "bundles: version, bundle_type, sale_price",
        """
        ALTER TABLE "{schema}"."bundles"
        ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1,
        ADD COLUMN IF NOT EXISTS bundle_type VARCHAR(30) NOT NULL DEFAULT 'production',
        ADD COLUMN IF NOT EXISTS sale_price NUMERIC(12, 2);
        """,
    ),
    (
        "bundles: unique (code, version)",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_bundle_code_version'
                AND conrelid = '"{schema}"."bundles"'::regclass
            ) THEN
                ALTER TABLE "{schema}"."bundles"
                DROP CONSTRAINT IF EXISTS bundles_code_key;
                ALTER TABLE "{schema}"."bundles"
                ADD CONSTRAINT uq_bundle_code_version UNIQUE (code, version);
            END IF;
        END $$;
        """,
    ),
    # --- Bundle Components ---
    (
        "bundle_components: multinivel columns",
        """
        ALTER TABLE "{schema}"."bundle_components"
        ADD COLUMN IF NOT EXISTS component_type VARCHAR(20) NOT NULL DEFAULT 'resource',
        ADD COLUMN IF NOT EXISTS component_bundle_id UUID REFERENCES "{schema}"."bundles"(id) ON DELETE CASCADE,
        ADD COLUMN IF NOT EXISTS phase_id UUID,
        ADD COLUMN IF NOT EXISTS waste_percent NUMERIC(5, 2) NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS season VARCHAR(50);
        """,
    ),
    # --- Production Orders ---
    (
        "production_orders: notes, start_date, end_date",
        """
        ALTER TABLE "{schema}"."production_orders"
        ADD COLUMN IF NOT EXISTS notes TEXT,
        ADD COLUMN IF NOT EXISTS start_date TIMESTAMPTZ,
        ADD COLUMN IF NOT EXISTS end_date TIMESTAMPTZ;
        """,
    ),
    (
        "production_orders: add exception_type and exception_notes",
        """
        ALTER TABLE "{schema}"."production_orders"
        ADD COLUMN IF NOT EXISTS exception_type VARCHAR(20),
        ADD COLUMN IF NOT EXISTS exception_notes TEXT;
        """,
    ),
    # --- Purchase Request Lines ---
    (
        "purchase_request_lines: quantity_received",
        """
        ALTER TABLE "{schema}"."purchase_request_lines"
        ADD COLUMN IF NOT EXISTS quantity_received NUMERIC(14, 4) NOT NULL DEFAULT 0;
        """,
    ),
    # --- Supplier Resources ---
    (
        "supplier_resources: offer columns",
        """
        ALTER TABLE "{schema}"."supplier_resources"
        ADD COLUMN IF NOT EXISTS unit_price NUMERIC(12, 4),
        ADD COLUMN IF NOT EXISTS currency_id UUID,
        ADD COLUMN IF NOT EXISTS lead_time_days INTEGER,
        ADD COLUMN IF NOT EXISTS min_quantity NUMERIC(14, 4),
        ADD COLUMN IF NOT EXISTS valid_until TIMESTAMPTZ;
        """,
    ),
    # --- Stock Reservations ---
    (
        "stock_reservations: table",
        """
        CREATE TABLE IF NOT EXISTS "{schema}"."stock_reservations" (
            id UUID PRIMARY KEY,
            warehouse_id UUID NOT NULL REFERENCES "{schema}"."warehouses"(id) ON DELETE CASCADE,
            resource_id UUID NOT NULL REFERENCES "{schema}"."resources"(id) ON DELETE CASCADE,
            quantity NUMERIC(14, 4) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            reference VARCHAR(100),
            notes VARCHAR(255),
            needed_by TIMESTAMPTZ,
            created_by UUID,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """,
    ),
    # --- Bundle Phases ---
    (
        "bundle_phases: table",
        """
        CREATE TABLE IF NOT EXISTS "{schema}"."bundle_phases" (
            id UUID PRIMARY KEY,
            bundle_id UUID NOT NULL REFERENCES "{schema}"."bundles"(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            "order" INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """,
    ),
    # --- Plan Item Annexes ---
    (
        "plan_item_annexes: table",
        """
        CREATE TABLE IF NOT EXISTS "{schema}"."plan_item_annexes" (
            id UUID PRIMARY KEY,
            production_order_id UUID NOT NULL REFERENCES "{schema}"."production_orders"(id) ON DELETE CASCADE,
            annex_type VARCHAR(30) NOT NULL,
            resource_id UUID REFERENCES "{schema}"."resources"(id) ON DELETE SET NULL,
            quantity NUMERIC(14, 4),
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """,
    ),
    # --- Inventory Costing Method (en public.tenants) ---
    (
        "tenants: inventory_costing_method (public)",
        """
        ALTER TABLE public.tenants
        ADD COLUMN IF NOT EXISTS inventory_costing_method VARCHAR(20) NOT NULL DEFAULT 'fifo';
        """,
    ),
]


def _table_exists(db, schema: str, table: str) -> bool:
    result = db.execute(
        text("""
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = :schema AND table_name = :table
        """),
        {"schema": schema, "table": table},
    ).first()
    return result is not None


def migrate_all_tenants():
    """Aplica todas las migraciones a todos los tenants."""
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        print(f"Procesando {len(tenants)} tenants...\n")

        for tenant in tenants:
            schema = tenant.schema_name
            print(f"→ {tenant.name} ({schema})")

            # Verificar que el schema existe
            if not _table_exists(db, schema, "bundles"):
                print(f"  ⚠️  Tabla 'bundles' no existe. Saltando.")
                continue

            for name, sql_template in TENANT_MIGRATIONS:
                try:
                    sql = sql_template.format(schema=schema)
                    db.execute(text(sql))
                    db.commit()
                    print(f"  ✅ {name}")
                except Exception as e:
                    db.rollback()
                    print(f"  ❌ {name}: {str(e)[:100]}")

            print()

        print("✅ Migraciones aplicadas a todos los tenants.")

    except Exception as e:
        print(f"\n❌ Error general: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    migrate_all_tenants()