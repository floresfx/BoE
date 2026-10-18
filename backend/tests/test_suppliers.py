"""Tests del módulo Supplier."""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


def _create_operational_tables(db: Session, schema: str) -> None:
    """Crea las tablas operativas necesarias para tests."""
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema}"."resources" (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            resource_type VARCHAR(30) NOT NULL,
            category_id UUID,
            subcategory_id UUID,
            base_unit_id UUID NOT NULL,
            cost NUMERIC(12, 2),
            waste_percent NUMERIC(5, 2) NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema}"."suppliers" (
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
        CREATE TABLE IF NOT EXISTS "{schema}"."supplier_resources" (
            id UUID PRIMARY KEY,
            supplier_id UUID NOT NULL REFERENCES "{schema}".suppliers(id) ON DELETE CASCADE,
            resource_id UUID NOT NULL REFERENCES "{schema}".resources(id) ON DELETE CASCADE,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (supplier_id, resource_id)
        )
    """))
    db.flush()


import pytest


@pytest.fixture
def tenant_sup(db: Session, tenant_factory):
    t = tenant_factory(name="Tenant Supplier Test")
    _create_operational_tables(db, t.schema_name)
    return t


def test_create_supplier(client: TestClient, tenant_sup, user_factory, token_for_user):
    user, _ = user_factory(tenant_sup)
    token = token_for_user(user)
    uid = uuid4().hex[:6]

    response = client.post(
        "/api/v1/suppliers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": f"PROV-{uid}",
            "name": f"Proveedor {uid}",
            "tax_id": "J-12345678-9",
            "email": f"contacto_{uid}@test.com",
            "phone": "0212-5551234",
            "address": "Av. Principal",
            "contact_name": "María Pérez",
            "notes": "Prueba",
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["code"] == f"PROV-{uid}"
    assert data["name"] == f"Proveedor {uid}"
    assert data["resources"] == []


def test_create_supplier_code_duplicado(
    client: TestClient, tenant_sup, user_factory, token_for_user
):
    user, _ = user_factory(tenant_sup)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"PROV-{uuid4().hex[:6]}"

    r1 = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"code": code, "name": "Proveedor 1"},
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"code": code, "name": "Proveedor 2"},
    )
    assert r2.status_code == 400


def test_list_suppliers(client: TestClient, tenant_sup, user_factory, token_for_user):
    user, _ = user_factory(tenant_sup)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(3):
        client.post(
            "/api/v1/suppliers",
            headers=headers,
            json={
                "code": f"PROV-{uuid4().hex[:6]}",
                "name": f"Proveedor {i}",
            },
        )

    response = client.get("/api/v1/suppliers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3


def test_update_supplier(client: TestClient, tenant_sup, user_factory, token_for_user):
    user, _ = user_factory(tenant_sup)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"code": f"PROV-{uuid4().hex[:6]}", "name": "Original"},
    ).json()

    response = client.put(
        f"/api/v1/suppliers/{created['id']}",
        headers=headers,
        json={"name": "Actualizado"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Actualizado"


def test_soft_delete_supplier(
    client: TestClient, tenant_sup, user_factory, token_for_user
):
    user, _ = user_factory(tenant_sup)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"code": f"PROV-{uuid4().hex[:6]}", "name": "A borrar"},
    ).json()

    response = client.delete(f"/api/v1/suppliers/{created['id']}", headers=headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/suppliers/{created['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_aislamiento_suppliers(
    client: TestClient, tenant_sup, tenant_factory, user_factory, token_for_user, db
):
    """Los suppliers de un tenant no se ven desde otro."""
    from tests.test_suppliers import _create_operational_tables

    tenant_b = tenant_factory(name="Tenant B Supplier")
    _create_operational_tables(db, tenant_b.schema_name)

    user_a, _ = user_factory(tenant_sup)
    user_b, _ = user_factory(tenant_b)
    token_a = token_for_user(user_a)
    token_b = token_for_user(user_b)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    client.post(
        "/api/v1/suppliers",
        headers=headers_a,
        json={"code": f"PROV-A-{uuid4().hex[:6]}", "name": "Proveedor A"},
    )
    client.post(
        "/api/v1/suppliers",
        headers=headers_b,
        json={"code": f"PROV-B-{uuid4().hex[:6]}", "name": "Proveedor B"},
    )

    list_a = client.get("/api/v1/suppliers", headers=headers_a).json()
    names_a = [s["name"] for s in list_a["items"]]
    assert "Proveedor A" in names_a
    assert "Proveedor B" not in names_a

    list_b = client.get("/api/v1/suppliers", headers=headers_b).json()
    names_b = [s["name"] for s in list_b["items"]]
    assert "Proveedor B" in names_b
    assert "Proveedor A" not in names_b

    # ---------------------------------------------------------------------------
# Tests de ofertas
# ---------------------------------------------------------------------------

def test_add_resource_with_offer(
    client: TestClient, tenant_sup, user_factory, token_for_user, unit
):
    """Añadir un recurso con datos de oferta."""
    import pytest

    # Necesitamos un recurso en el tenant
    user, _ = user_factory(tenant_sup)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    # Crear un recurso
    from uuid import uuid4
    resource_response = client.post(
        "/api/v1/resources",
        headers=headers,
        json={
            "name": f"Recurso {uuid4().hex[:6]}",
            "resource_type": "materia_prima",
            "base_unit_id": str(unit.id),
        },
    )
    assert resource_response.status_code == 201, resource_response.json()
    resource_id = resource_response.json()["id"]

    # Crear supplier
    supplier_response = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={
            "code": f"PROV-{uuid4().hex[:6]}",
            "name": "Proveedor Test",
        },
    )
    assert supplier_response.status_code == 201
    supplier_id = supplier_response.json()["id"]

    # Añadir recurso con oferta
    response = client.post(
        f"/api/v1/suppliers/{supplier_id}/resources",
        headers=headers,
        json={
            "resource_id": resource_id,
            "unit_price": "5.50",
            "lead_time_days": 3,
            "min_quantity": "10",
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["resource_id"] == resource_id
    assert data["unit_price"] == "5.5000"
    assert data["lead_time_days"] == 3
    assert data["min_quantity"] == "10.0000"


def _create_operational_tables(db: Session, schema: str) -> None:
    """Crea las tablas operativas necesarias para tests."""
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema}"."resources" (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            resource_type VARCHAR(30) NOT NULL,
            category_id UUID,
            subcategory_id UUID,
            base_unit_id UUID NOT NULL,
            cost NUMERIC(12, 2),
            waste_percent NUMERIC(5, 2) NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema}"."suppliers" (
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
        CREATE TABLE IF NOT EXISTS "{schema}"."supplier_resources" (
            id UUID PRIMARY KEY,
            supplier_id UUID NOT NULL REFERENCES "{schema}".suppliers(id) ON DELETE CASCADE,
            resource_id UUID NOT NULL REFERENCES "{schema}".resources(id) ON DELETE CASCADE,
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
    db.flush()