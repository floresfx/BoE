"""Aplica migraciones Alembic a todos los schemas de tenants.

Uso:
    cd backend
    python -m scripts.migrate_tenants

Requiere que ALEMBIC_TARGET=tenant:<schema> funcione en alembic/env.py.
"""

import os
import subprocess
import sys

from sqlalchemy import text

from app.core.database import SessionLocal


def _list_tenant_schemas() -> list[str]:
    db = SessionLocal()
    try:
        rows = db.execute(
            text(
                "SELECT schema_name FROM public.tenants "
                "WHERE status = 'activo' ORDER BY created_at"
            )
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        db.close()


def _run_alembic_for(schema: str) -> None:
    env = os.environ.copy()
    env["ALEMBIC_TARGET"] = f"tenant:{schema}"
    print(f"\n▶ Migrando schema: {schema}")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"❌ Error en {schema}:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout)


def main() -> None:
    schemas = _list_tenant_schemas()
    if not schemas:
        print("No hay tenants activos.")
        return

    print(f"Encontrados {len(schemas)} tenants.")
    for schema in schemas:
        _run_alembic_for(schema)

    print("\n✅ Migraciones completadas.")


if __name__ == "__main__":
    main()