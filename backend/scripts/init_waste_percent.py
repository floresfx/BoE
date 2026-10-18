"""Añade la columna waste_percent a resources en todos los tenants existentes."""
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models import Tenant

def init_waste_percent() -> None:
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for tenant in tenants:
            schema = tenant.schema_name
            print(f"Procesando {tenant.name} ({schema})...")
            db.execute(text(f"""
                ALTER TABLE "{schema}"."resources"
                ADD COLUMN IF NOT EXISTS waste_percent NUMERIC(5, 2) NOT NULL DEFAULT 0
            """))
            db.commit()
            print(f"  ✓ {schema} listo")
        print(f"\n✅ {len(tenants)} tenants procesados")
    finally:
        db.close()

if __name__ == "__main__":
    init_waste_percent()