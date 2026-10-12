"""Inicializa la tabla `resources` en cada schema de tenant existente.

Este script es TEMPORAL. Se reemplazará por Alembic multi-schema
en la Fase 2 del proyecto.

Uso:
    cd backend
    python -m scripts.init_tenant_schemas
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal


# SQL para crear la tabla `resources` en un schema dado.
# OJO: coincide EXACTAMENTE con el modelo Resource de SQLAlchemy.
CREATE_RESOURCES_SQL = """
CREATE TABLE IF NOT EXISTS "{schema}"."resources" (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    resource_type VARCHAR(30) NOT NULL,
    category VARCHAR(100),
    base_unit VARCHAR(20) NOT NULL,
    cost NUMERIC(12, 2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_resource_name
    ON "{schema}"."resources" (name);
CREATE INDEX IF NOT EXISTS ix_resource_type
    ON "{schema}"."resources" (resource_type);
CREATE INDEX IF NOT EXISTS ix_resource_is_active
    ON "{schema}"."resources" (is_active);
"""


def _list_tenant_schemas(db: Session) -> list[str]:
    """Devuelve los schema_name de todos los tenants activos."""
    rows = db.execute(
        text(
            "SELECT schema_name FROM public.tenants "
            "WHERE status = 'activo' ORDER BY created_at"
        )
    ).fetchall()
    return [row[0] for row in rows]


def init_all_tenants() -> None:
    """Crea la tabla `resources` en cada schema de tenant."""
    db = SessionLocal()
    try:
        schemas = _list_tenant_schemas(db)
        if not schemas:
            print("No hay tenants activos.")
            return

        print(f"Encontrados {len(schemas)} tenants.")
        for schema in schemas:
            # Validación mínima por seguridad
            if not schema.replace("_", "").isalnum():
                print(f"  ⚠ Schema inválido, saltando: {schema}")
                continue

            print(f"  ▶ Inicializando schema: {schema}")
            db.execute(text(CREATE_RESOURCES_SQL.format(schema=schema)))

        db.commit()
        print(f"\n✅ {len(schemas)} schemas inicializados.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_all_tenants()