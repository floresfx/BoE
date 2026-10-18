"""Tests del modelo Resource (Fase 2: con FKs y N:M).

Verifica:
1. CRUD básico de resources con FKs.
2. Aislamiento entre tenants.
3. Filtros de listado.
4. Soft delete.
5. Gestión de atributos (N:M).
6. Gestión de impuestos (N:M).
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------------------------------------------------------------------------
# Helper: crea la tabla resources en un schema de test (con FKs)
# ---------------------------------------------------------------------------

def _create_resources_tables(db: Session, schema: str) -> None:
    """Crea las tablas operativas en el schema dado (idempotente)."""
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
        CREATE TABLE IF NOT EXISTS "{schema}"."resources_attributes" (
            id UUID PRIMARY KEY,
            resource_id UUID NOT NULL REFERENCES "{schema}".resources(id) ON DELETE CASCADE,
            attribute_id UUID NOT NULL,
            value TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (resource_id, attribute_id)
        )
    """))
    db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS "{schema}"."resources_taxes" (
            id UUID PRIMARY KEY,
            resource_id UUID NOT NULL REFERENCES "{schema}".resources(id) ON DELETE CASCADE,
            tax_id UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (resource_id, tax_id)
        )
    """))
    db.flush()


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

@pytest.fixture
def tenant_a(db: Session, tenant_factory):
    """Tenant A con tablas operativas creadas."""
    t = tenant_factory(name="Tenant A")
    _create_resources_tables(db, t.schema_name)
    return t


@pytest.fixture
def tenant_b(db: Session, tenant_factory):
    """Tenant B con tablas operativas creadas."""
    t = tenant_factory(name="Tenant B")
    _create_resources_tables(db, t.schema_name)
    return t


# ---------------------------------------------------------------------------
# Tests CRUD básico
# ---------------------------------------------------------------------------

def test_create_resource(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, category
):
    """Crear un resource con FKs."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    response = client.post(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Harina de trigo",
            "resource_type": "materia_prima",
            "category_id": str(category.id),
            "base_unit_id": str(unit.id),
            "cost": "2.50",
            "is_active": True,
        },
    )

    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["name"] == "Harina de trigo"
    assert data["resource_type"] == "materia_prima"
    assert data["category_id"] == str(category.id)
    assert data["base_unit_id"] == str(unit.id)
    assert float(data["cost"]) == 2.50


def test_create_resource_tipo_invalido(
    client: TestClient, tenant_a, user_factory, token_for_user, unit
):
    """Tipo de recurso inválido → 422."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    response = client.post(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "X",
            "resource_type": "tipo_que_no_existe",
            "base_unit_id": str(unit.id),
        },
    )
    assert response.status_code == 422


def test_create_resource_fk_invalida(
    client: TestClient, tenant_a, user_factory, token_for_user, unit
):
    """FK inválida → 400."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    response = client.post(
        "/api/v1/resources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Y",
            "resource_type": "materia_prima",
            "base_unit_id": str(uuid4()),  # ← no existe
        },
    )
    assert response.status_code == 400


def test_list_resources(
    client: TestClient, tenant_a, user_factory, token_for_user, unit
):
    """Listar resources del tenant."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    for name in ["Harina", "Azúcar"]:
        client.post(
            "/api/v1/resources",
            headers=headers,
            json={
                "name": name,
                "resource_type": "materia_prima",
                "base_unit_id": str(unit.id),
            },
        )

    response = client.get("/api/v1/resources", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    names = sorted(r["name"] for r in data["items"])
    assert names == ["Azúcar", "Harina"]


def test_list_resources_con_filtro_tipo(
    client: TestClient, tenant_a, user_factory, token_for_user, unit
):
    """Filtrar por resource_type."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Harina", "resource_type": "materia_prima", "base_unit_id": str(unit.id)},
    )
    client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Corte de pelo", "resource_type": "servicio_propio", "base_unit_id": str(unit.id)},
    )

    response = client.get(
        "/api/v1/resources?resource_type=materia_prima", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Harina"


def test_update_resource(
    client: TestClient, tenant_a, user_factory, token_for_user, unit
):
    """Actualizar un resource."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Harina", "resource_type": "materia_prima", "base_unit_id": str(unit.id)},
    ).json()

    response = client.put(
        f"/api/v1/resources/{created['id']}",
        headers=headers,
        json={"cost": "3.75"},
    )
    assert response.status_code == 200
    assert float(response.json()["cost"]) == 3.75


def test_soft_delete_resource(
    client: TestClient, tenant_a, user_factory, token_for_user, unit
):
    """Soft delete: marca is_active=False pero no borra."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Harina", "resource_type": "materia_prima", "base_unit_id": str(unit.id)},
    ).json()

    response = client.delete(
        f"/api/v1/resources/{created['id']}", headers=headers
    )
    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/resources/{created['id']}", headers=headers
    )
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


# ---------------------------------------------------------------------------
# Test crítico: aislamiento
# ---------------------------------------------------------------------------

def test_resources_aislados_por_tenant(
    client: TestClient, tenant_a, tenant_b, user_factory, token_for_user, unit
):
    """Un tenant NO ve los resources de otro."""
    user_a, _ = user_factory(tenant_a)
    user_b, _ = user_factory(tenant_b)
    token_a = token_for_user(user_a)
    token_b = token_for_user(user_b)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    r_a = client.post(
        "/api/v1/resources",
        headers=headers_a,
        json={"name": "Recurso de A", "resource_type": "materia_prima", "base_unit_id": str(unit.id)},
    )
    assert r_a.status_code == 201, r_a.json()

    r_b = client.post(
        "/api/v1/resources",
        headers=headers_b,
        json={"name": "Recurso de B", "resource_type": "insumo", "base_unit_id": str(unit.id)},
    )
    assert r_b.status_code == 201, r_b.json()

    list_a = client.get("/api/v1/resources", headers=headers_a)
    names_a = [r["name"] for r in list_a.json()["items"]]
    assert "Recurso de A" in names_a
    assert "Recurso de B" not in names_a, "FUGA: A ve el recurso de B"

    list_b = client.get("/api/v1/resources", headers=headers_b)
    names_b = [r["name"] for r in list_b.json()["items"]]
    assert "Recurso de B" in names_b
    assert "Recurso de A" not in names_b, "FUGA: B ve el recurso de A"

    cross = client.get(
        f"/api/v1/resources/{r_b.json()['id']}", headers=headers_a
    )
    assert cross.status_code == 404, "FUGA: A accede al recurso de B"


# ---------------------------------------------------------------------------
# Tests de atributos
# ---------------------------------------------------------------------------

def test_assign_attribute_to_resource(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, attribute
):
    """Asignar un atributo a un recurso."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    resource = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Prótesis", "resource_type": "producto_terminado", "base_unit_id": str(unit.id)},
    ).json()

    response = client.post(
        f"/api/v1/resources/{resource['id']}/attributes",
        headers=headers,
        json={"attribute_id": str(attribute.id), "value": "true"},
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["attribute_id"] == str(attribute.id)
    assert data["value"] == "true"


def test_assign_duplicate_attribute_fails(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, attribute
):
    """Asignar el mismo atributo dos veces → 400."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    resource = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Prótesis", "resource_type": "producto_terminado", "base_unit_id": str(unit.id)},
    ).json()

    client.post(
        f"/api/v1/resources/{resource['id']}/attributes",
        headers=headers,
        json={"attribute_id": str(attribute.id), "value": "true"},
    )

    response = client.post(
        f"/api/v1/resources/{resource['id']}/attributes",
        headers=headers,
        json={"attribute_id": str(attribute.id), "value": "false"},
    )
    assert response.status_code == 400


def test_list_resource_attributes(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, attribute
):
    """Listar atributos de un recurso."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    resource = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Prótesis", "resource_type": "producto_terminado", "base_unit_id": str(unit.id)},
    ).json()

    client.post(
        f"/api/v1/resources/{resource['id']}/attributes",
        headers=headers,
        json={"attribute_id": str(attribute.id), "value": "true"},
    )

    response = client.get(
        f"/api/v1/resources/{resource['id']}/attributes", headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_remove_attribute_from_resource(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, attribute
):
    """Quitar un atributo de un recurso."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    resource = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Prótesis", "resource_type": "producto_terminado", "base_unit_id": str(unit.id)},
    ).json()

    client.post(
        f"/api/v1/resources/{resource['id']}/attributes",
        headers=headers,
        json={"attribute_id": str(attribute.id), "value": "true"},
    )

    response = client.delete(
        f"/api/v1/resources/{resource['id']}/attributes/{attribute.id}",
        headers=headers,
    )
    assert response.status_code == 204

    list_response = client.get(
        f"/api/v1/resources/{resource['id']}/attributes", headers=headers
    )
    assert len(list_response.json()) == 0


# ---------------------------------------------------------------------------
# Tests de impuestos
# ---------------------------------------------------------------------------

def test_assign_tax_to_resource(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, tax
):
    """Asignar un impuesto a un recurso."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    resource = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Medicamento", "resource_type": "producto_terminado", "base_unit_id": str(unit.id)},
    ).json()

    response = client.post(
        f"/api/v1/resources/{resource['id']}/taxes",
        headers=headers,
        json={"tax_id": str(tax.id)},
    )
    assert response.status_code == 201, response.json()
    assert response.json()["tax_id"] == str(tax.id)


def test_remove_tax_from_resource(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, tax
):
    """Quitar un impuesto de un recurso."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    resource = client.post(
        "/api/v1/resources",
        headers=headers,
        json={"name": "Medicamento", "resource_type": "producto_terminado", "base_unit_id": str(unit.id)},
    ).json()

    client.post(
        f"/api/v1/resources/{resource['id']}/taxes",
        headers=headers,
        json={"tax_id": str(tax.id)},
    )

    response = client.delete(
        f"/api/v1/resources/{resource['id']}/taxes/{tax.id}", headers=headers
    )
    assert response.status_code == 204


# ---------------------------------------------------------------------------
# Test: create con atributos y taxes inline
# ---------------------------------------------------------------------------

def test_create_resource_with_inline_attributes_and_taxes(
    client: TestClient, tenant_a, user_factory, token_for_user, unit, attribute, tax
):
    """Crear un recurso con atributos y taxes inline (transaccional)."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/resources",
        headers=headers,
        json={
            "name": "Prótesis con todo",
            "resource_type": "producto_terminado",
            "base_unit_id": str(unit.id),
            "attributes": [
                {"attribute_id": str(attribute.id), "value": "true"}
            ],
            "taxes": [
                {"tax_id": str(tax.id)}
            ],
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert len(data["attributes"]) == 1
    assert len(data["taxes"]) == 1

    # ---------------------------------------------------------------------------
# Test: límites por plan
# ---------------------------------------------------------------------------

def test_create_resource_excede_limite_plan(
    client: TestClient,
    tenant_a,
    user_factory,
    token_for_user,
    unit,
    currency,  # ← fixture que ya existe
    db: Session,
):
    """Crear más recursos que el límite del plan → 403."""
    from app.models import Plan, PlanLimit

    # Buscar plan "mpr_base" (ya existe vía seed)
    plan = db.query(Plan).filter(Plan.code == "mpr_base").first()

    # Si no existe, crear uno de prueba con currency real
    if not plan:
        plan = Plan(
            code="test_limit_plan",
            name="Test Limit Plan",
            price=0,
            currency_id=currency.id,  # ← FK válida
            interval="monthly",
            trial_days=0,
        )
        db.add(plan)
        db.flush()

    # Asegurar que tiene un límite de 1 recurso
    existing_limit = (
        db.query(PlanLimit)
        .filter(
            PlanLimit.plan_id == plan.id,
            PlanLimit.limit_code == "recursos",
        )
        .first()
    )
    if existing_limit:
        existing_limit.value = 1
    else:
        db.add(PlanLimit(plan_id=plan.id, limit_code="recursos", value=1))

    tenant_a.plan_id = plan.id
    db.flush()

    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    # Primer recurso → OK
    r1 = client.post(
        "/api/v1/resources",
        headers=headers,
        json={
            "name": "Recurso 1",
            "resource_type": "materia_prima",
            "base_unit_id": str(unit.id),
        },
    )
    assert r1.status_code == 201, r1.json()

    # Segundo recurso → 403
    r2 = client.post(
        "/api/v1/resources",
        headers=headers,
        json={
            "name": "Recurso 2",
            "resource_type": "materia_prima",
            "base_unit_id": str(unit.id),
        },
    )
    assert r2.status_code == 403, r2.json()
    detail = r2.json()["detail"].lower()
    assert "límite" in detail or "limite" in detail