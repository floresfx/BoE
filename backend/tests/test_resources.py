"""Tests del modelo Resource (operativo por tenant).

Verifica:
1. CRUD básico de resources.
2. Aislamiento entre tenants: A no ve recursos de B.
3. Filtros de listado.
4. Soft delete.
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------------------------------------------------------------------------
# Helper: crea la tabla resources en un schema de test
# ---------------------------------------------------------------------------

def _create_resources_table(db: Session, schema: str) -> None:
    """Crea la tabla resources en el schema dado (idempotente)."""
    db.execute(text(f"""
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
        )
    """))
    db.flush()


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

import pytest


@pytest.fixture
def tenant_a(db: Session, tenant_factory):
    """Tenant A con tabla resources creada."""
    t = tenant_factory(name="Tenant A")
    _create_resources_table(db, t.schema_name)
    return t


@pytest.fixture
def tenant_b(db: Session, tenant_factory):
    """Tenant B con tabla resources creada."""
    t = tenant_factory(name="Tenant B")
    _create_resources_table(db, t.schema_name)
    return t


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_resource(
    client: TestClient,
    tenant_a,
    user_factory,
    token_for_user,
):
    """Crear un resource en un tenant."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    response = client.post(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Harina de trigo",
            "resource_type": "materia_prima",
            "category": "harinas",
            "base_unit": "kg",
            "cost": "2.50",
            "is_active": True,
        },
    )

    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["name"] == "Harina de trigo"
    assert data["resource_type"] == "materia_prima"
    assert data["base_unit"] == "kg"
    assert float(data["cost"]) == 2.50


def test_create_resource_tipo_invalido(
    client: TestClient,
    tenant_a,
    user_factory,
    token_for_user,
):
    """Tipo de recurso inválido → 422 (Pydantic Literal)."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    response = client.post(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "X",
            "resource_type": "tipo_que_no_existe",
            "base_unit": "kg",
        },
    )

    assert response.status_code == 422


def test_list_resources(
    client: TestClient,
    tenant_a,
    user_factory,
    token_for_user,
):
    """Listar resources del tenant."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    # Crear dos
    for name in ["Harina", "Azúcar"]:
        client.post(
            "/api/v1/resources",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": name,
                "resource_type": "materia_prima",
                "base_unit": "kg",
            },
        )

    response = client.get(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    names = sorted(r["name"] for r in data["items"])
    assert names == ["Azúcar", "Harina"]


def test_list_resources_con_filtro_tipo(
    client: TestClient,
    tenant_a,
    user_factory,
    token_for_user,
):
    """Filtrar por resource_type."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    client.post(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Harina", "resource_type": "materia_prima", "base_unit": "kg"},
    )
    client.post(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Corte de pelo", "resource_type": "servicio_propio", "base_unit": "hora"},
    )

    response = client.get(
        "/api/v1/resources?resource_type=materia_prima",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Harina"


def test_update_resource(
    client: TestClient,
    tenant_a,
    user_factory,
    token_for_user,
):
    """Actualizar un resource."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Harina", "resource_type": "materia_prima", "base_unit": "kg"},
    ).json()

    response = client.put(
        f"/api/v1/resources/{created['id']}",
        headers=headers,
        json={"cost": "3.75"},
    )
    assert response.status_code == 200
    assert float(response.json()["cost"]) == 3.75


def test_soft_delete_resource(
    client: TestClient,
    tenant_a,
    user_factory,
    token_for_user,
):
    """Soft delete: marca is_active=False pero no borra."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Harina", "resource_type": "materia_prima", "base_unit": "kg"},
    ).json()

    response = client.delete(
        f"/api/v1/resources/{created['id']}",
        headers=headers,
    )
    assert response.status_code == 204

    # Sigue existiendo pero inactivo
    get_response = client.get(
        f"/api/v1/resources/{created['id']}",
        headers=headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


# ---------------------------------------------------------------------------
# ⭐ TEST CRÍTICO: aislamiento entre tenants
# ---------------------------------------------------------------------------

def test_resources_aislados_por_tenant(
    client: TestClient,
    tenant_a,
    tenant_b,
    user_factory,
    token_for_user,
):
    """Un tenant NO ve los resources de otro.

    Este es el test que verifica que el `SET LOCAL search_path` funciona
    con un modelo operativo real.
    """
    user_a, _ = user_factory(tenant_a)
    user_b, _ = user_factory(tenant_b)
    token_a = token_for_user(user_a)
    token_b = token_for_user(user_b)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant A crea un recurso
    r_a = client.post(
        "/api/v1/resources",
        headers=headers_a,
        json={
            "name": "Recurso de A",
            "resource_type": "materia_prima",
            "base_unit": "kg",
        },
    )
    assert r_a.status_code == 201, r_a.json()

    # Tenant B crea otro recurso
    r_b = client.post(
        "/api/v1/resources",
        headers=headers_b,
        json={
            "name": "Recurso de B",
            "resource_type": "insumo",
            "base_unit": "unidad",
        },
    )
    assert r_b.status_code == 201, r_b.json()

    # A lista sus recursos → solo ve el suyo
    list_a = client.get("/api/v1/resources", headers=headers_a)
    assert list_a.status_code == 200
    items_a = list_a.json()["items"]
    names_a = [r["name"] for r in items_a]

    assert "Recurso de A" in names_a
    assert "Recurso de B" not in names_a, "FUGA: A ve el recurso de B"
    assert list_a.json()["total"] == 1

    # B lista sus recursos → solo ve el suyo
    list_b = client.get("/api/v1/resources", headers=headers_b)
    assert list_b.status_code == 200
    items_b = list_b.json()["items"]
    names_b = [r["name"] for r in items_b]

    assert "Recurso de B" in names_b
    assert "Recurso de A" not in names_b, "FUGA: B ve el recurso de A"
    assert list_b.json()["total"] == 1

    # A intenta acceder al recurso de B por ID → 404
    cross = client.get(
        f"/api/v1/resources/{r_b.json()['id']}",
        headers=headers_a,
    )
    assert cross.status_code == 404, "FUGA: A accede al recurso de B"