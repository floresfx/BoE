"""Servicio para gestionar tenants.

Centraliza la lógica de creación de tenants: crear el schema en
PostgreSQL, crear el tenant en public, etc.
"""

from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Tenant


def _validate_schema_name(schema_name: str) -> None:
    """Valida que el schema_name sea seguro (solo letras, números, _)."""
    if not schema_name.replace("_", "").isalnum():
        raise ValueError(f"Schema inválido: {schema_name}")


def generate_schema_name() -> str:
    """Genera un schema_name único."""
    return f"tenant_{uuid4().hex[:16]}"


def create_tenant_schema(db: Session, schema_name: str) -> None:
    """Crea el schema del tenant en PostgreSQL.

    También crea las tablas operativas dentro del schema.
    """
    _validate_schema_name(schema_name)

    # Crear schema
    db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    # Crear tablas operativas dentro del schema
    # (por ahora solo resources, resources_attributes, resources_taxes)
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."resources" (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            resource_type VARCHAR(30) NOT NULL,
            category_id UUID,
            subcategory_id UUID,
            base_unit_id UUID NOT NULL,
            waste_percent NUMERIC(5, 2) NOT NULL DEFAULT 0,
            cost NUMERIC(12, 2),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."resources_attributes" (
            id UUID PRIMARY KEY,
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id) ON DELETE CASCADE,
            attribute_id UUID NOT NULL,
            value TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (resource_id, attribute_id)
        )
    """))
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."resources_taxes" (
            id UUID PRIMARY KEY,
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id) ON DELETE CASCADE,
            tax_id UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (resource_id, tax_id)
        )
    """))
    
    # Warehouses
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."warehouses" (
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
        CREATE TABLE IF NOT EXISTS "{schema_name}"."stock_lots" (
            id UUID PRIMARY KEY,
            warehouse_id UUID NOT NULL REFERENCES "{schema_name}".warehouses(id),
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id),
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
        CREATE TABLE IF NOT EXISTS "{schema_name}"."movements" (
            id UUID PRIMARY KEY,
            warehouse_id UUID NOT NULL REFERENCES "{schema_name}".warehouses(id),
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id),
            lot_id UUID REFERENCES "{schema_name}".stock_lots(id),
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

    # Suppliers
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."suppliers" (
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
        CREATE TABLE IF NOT EXISTS "{schema_name}"."supplier_resources" (
            id UUID PRIMARY KEY,
            supplier_id UUID NOT NULL REFERENCES "{schema_name}".suppliers(id) ON DELETE CASCADE,
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id) ON DELETE CASCADE,
            unit_price NUMERIC(12, 4),
            currency_id UUID,
            lead_time_days INTEGER,
            min_quantity NUMERIC(14, 4),
            valid_until TIMESTAMPTZ,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (supplier_id, resource_id)
        )
    """))

        # Bundles
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."bundles" (
            id UUID PRIMARY KEY,
            code VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category_id UUID,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (code)
        )
    """))

    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."bundle_components" (
            id UUID PRIMARY KEY,
            bundle_id UUID NOT NULL REFERENCES "{schema_name}".bundles(id) ON DELETE CASCADE,
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id) ON DELETE CASCADE,
            quantity NUMERIC(14, 4) NOT NULL,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (bundle_id, resource_id)
        )
    """))

    # Purchase Requests
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."purchase_requests" (
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
        CREATE TABLE IF NOT EXISTS "{schema_name}"."purchase_request_lines" (
            id UUID PRIMARY KEY,
            request_id UUID NOT NULL REFERENCES "{schema_name}".purchase_requests(id) ON DELETE CASCADE,
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id),
            quantity NUMERIC(14, 4) NOT NULL,
            quantity_received NUMERIC(14, 4) NOT NULL DEFAULT 0,
            supplier_id UUID REFERENCES "{schema_name}".suppliers(id) ON DELETE SET NULL,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (request_id, resource_id)
        )
    """))
    
    # Supplier Quotes
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."supplier_quotes" (
            id UUID PRIMARY KEY,
            request_id UUID NOT NULL REFERENCES "{schema_name}".purchase_requests(id) ON DELETE CASCADE,
            line_id UUID NOT NULL REFERENCES "{schema_name}".purchase_request_lines(id) ON DELETE CASCADE,
            supplier_id UUID NOT NULL REFERENCES "{schema_name}".suppliers(id) ON DELETE CASCADE,
            unit_price NUMERIC(12, 4) NOT NULL,
            currency_code VARCHAR(10) NOT NULL DEFAULT 'USD',
            lead_time_days INTEGER NOT NULL DEFAULT 0,
            valid_until TIMESTAMPTZ,
            notes TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            is_selected BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))

    # Purchase Orders
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."purchase_orders" (
            id UUID PRIMARY KEY,
            code VARCHAR(50) NOT NULL,
            request_id UUID REFERENCES "{schema_name}".purchase_requests(id) ON DELETE SET NULL,
            supplier_id UUID NOT NULL REFERENCES "{schema_name}".suppliers(id) ON DELETE RESTRICT,
            status VARCHAR(20) NOT NULL DEFAULT 'draft',
            total NUMERIC(14, 4) NOT NULL DEFAULT 0,
            currency_code VARCHAR(10) NOT NULL DEFAULT 'USD',
            expected_delivery TIMESTAMPTZ,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (code)
        )
    """))

    # Purchase Order Lines
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema_name}"."purchase_order_lines" (
            id UUID PRIMARY KEY,
            order_id UUID NOT NULL REFERENCES "{schema_name}".purchase_orders(id) ON DELETE CASCADE,
            resource_id UUID NOT NULL REFERENCES "{schema_name}".resources(id) ON DELETE RESTRICT,
            quantity NUMERIC(14, 4) NOT NULL,
            unit_price NUMERIC(12, 4) NOT NULL,
            subtotal NUMERIC(14, 4) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))

    db.flush()


def drop_tenant_schema(db: Session, schema_name: str) -> None:
    """Elimina el schema del tenant. Usar con cuidado."""
    _validate_schema_name(schema_name)
    db.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
    db.flush()


def create_tenant_with_schema(db: Session, tenant: Tenant) -> Tenant:
    """Crea el schema del tenant y lo persiste.

    Args:
        db: sesión SQLAlchemy (sin search_path de tenant, opera en public).
        tenant: instancia de Tenant (sin schema_name asignado).

    Returns:
        El tenant con schema_name asignado y persistido.
    """
    if not tenant.schema_name:
        tenant.schema_name = generate_schema_name()

    # 1. Crear el schema en PostgreSQL
    create_tenant_schema(db, tenant.schema_name)

    # 2. Persistir el tenant en public
    db.add(tenant)
    db.flush()

    return tenant