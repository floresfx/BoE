"""Script para crear la tabla stock_reservations en todos los tenants existentes."""

from sqlalchemy import text
from app.core.database import SessionLocal
from app.models import Tenant


def create_reservation_tables():
    """Itera sobre todos los tenants y crea la tabla si no existe."""
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        print(f"Procesando {len(tenants)} tenants...")

        for tenant in tenants:
            schema = tenant.schema_name
            print(f"  → {tenant.name} ({schema})")

            db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{schema}"."stock_reservations" (
                    id UUID PRIMARY KEY,
                    warehouse_id UUID NOT NULL REFERENCES "{schema}".warehouses(id) ON DELETE CASCADE,
                    resource_id UUID NOT NULL REFERENCES "{schema}".resources(id) ON DELETE CASCADE,
                    quantity NUMERIC(14, 4) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    reference VARCHAR(100),
                    notes VARCHAR(255),
                    needed_by TIMESTAMPTZ,
                    created_by UUID,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """))
            db.commit()

        print("\n✅ Tablas de reservas creadas en todos los tenants.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_reservation_tables()