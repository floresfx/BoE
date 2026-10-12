"""Script para probar el middleware de tenant."""

from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.tenant_context import clear_tenant_schema, set_tenant_schema


def test_tenant_schema():
    """Prueba el SET search_path."""
    db = SessionLocal()

    try:
        # 1. Sin tenant
        result = db.execute(text("SHOW search_path"))
        print(f"Sin tenant: {result.scalar()}")

        # 2. Con tenant
        set_tenant_schema("tenant_test123")
        db.close()

        db = SessionLocal()
        db.execute(text("SET search_path TO tenant_test123, public"))
        result = db.execute(text("SHOW search_path"))
        print(f"Con tenant: {result.scalar()}")

        # 3. Limpiar
        clear_tenant_schema()
        db.close()

        db = SessionLocal()
        result = db.execute(text("SHOW search_path"))
        print(f"Sin tenant: {result.scalar()}")

    finally:
        db.close()


if __name__ == "__main__":
    test_tenant_schema()