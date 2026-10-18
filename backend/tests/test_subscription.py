"""Tests de los endpoints de suscripción.

Verifica:
1. GET /subscription/plans (público) → devuelve 5 planes.
2. GET /subscription/current (auth) → estado del tenant.
3. POST /subscription/select-plan (auth) → activa plan + trial.
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import pytest
from sqlalchemy import text


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
    db.flush()


@pytest.fixture
def tenant_a(db: Session, tenant_factory):
    """Tenant A con tablas operativas creadas."""
    t = tenant_factory(name="Tenant A")
    _create_resources_tables(db, t.schema_name)
    return t


def test_list_plans_publico(client: TestClient):
    """Listar planes es público (no requiere auth)."""
    response = client.get("/api/v1/subscription/plans")
    assert response.status_code == 200
    plans = response.json()

    assert len(plans) == 5
    codes = {p["code"] for p in plans}
    assert codes == {"mpr_base", "mpr_plus", "mp_gratuito", "mp_basico", "mp_plus"}

    # Verificar estructura
    for plan in plans:
        assert "id" in plan
        assert "name" in plan
        assert "price" in plan
        assert "interval" in plan
        assert "trial_days" in plan
        assert "features" in plan
        assert "limits" in plan


def test_list_plans_incluye_trial_mpr(client: TestClient):
    """Los planes MPR tienen trial_days = 14."""
    response = client.get("/api/v1/subscription/plans")
    plans = response.json()

    mpr_plans = [p for p in plans if p["code"].startswith("mpr_")]
    assert len(mpr_plans) == 2
    for p in mpr_plans:
        assert p["trial_days"] == 14

    mp_plans = [p for p in plans if p["code"].startswith("mp_")]
    for p in mp_plans:
        assert p["trial_days"] == 0


def test_current_sin_plan(
    client: TestClient, tenant_a, user_factory, token_for_user
):
    """Sin plan → status = 'sin_plan'."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    response = client.get(
        "/api/v1/subscription/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sin_plan"
    assert data["plan_id"] is None
    assert data["plan_name"] is None
    assert data["days_remaining"] is None


def test_current_requiere_auth(client: TestClient):
    """Sin token → 403."""
    response = client.get("/api/v1/subscription/current")
    assert response.status_code in (401, 403)


def test_select_plan_activa_trial(
    client: TestClient, tenant_a, user_factory, token_for_user, db: Session
):
    """Seleccionar un plan MPR activa trial de 14 días."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener plan mpr_base
    plans = client.get("/api/v1/subscription/plans").json()
    mpr_base = next(p for p in plans if p["code"] == "mpr_base")

    # Seleccionar
    response = client.post(
        "/api/v1/subscription/select-plan",
        headers=headers,
        json={"plan_id": mpr_base["id"]},
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["plan_id"] == mpr_base["id"]
    assert data["plan_name"] == "MPR Base"
    assert data["status"] == "trial"
    assert data["trial_ends_at"] is not None
    assert "14" in data["message"]

    # Verificar current
    current = client.get("/api/v1/subscription/current", headers=headers)
    assert current.status_code == 200
    current_data = current.json()
    assert current_data["status"] == "trial"
    assert current_data["plan_id"] == mpr_base["id"]
    assert current_data["days_remaining"] in (13, 14)


def test_select_plan_sin_trial(
    client: TestClient, tenant_a, user_factory, token_for_user
):
    """Seleccionar un plan sin trial → status = 'activo'."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)
    headers = {"Authorization": f"Bearer {token}"}

    plans = client.get("/api/v1/subscription/plans").json()
    mp_gratuito = next(p for p in plans if p["code"] == "mp_gratuito")

    response = client.post(
        "/api/v1/subscription/select-plan",
        headers=headers,
        json={"plan_id": mp_gratuito["id"]},
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["status"] == "activo"
    assert data["trial_ends_at"] is None


def test_select_plan_invalido(
    client: TestClient, tenant_a, user_factory, token_for_user
):
    """Plan que no existe → 404."""
    user, _ = user_factory(tenant_a)
    token = token_for_user(user)

    response = client.post(
        "/api/v1/subscription/select-plan",
        headers={"Authorization": f"Bearer {token}"},
        json={"plan_id": str(uuid4())},
    )
    assert response.status_code == 404


def test_select_plan_requiere_auth(client: TestClient):
    """Sin token → 403."""
    response = client.post(
        "/api/v1/subscription/select-plan",
        json={"plan_id": str(uuid4())},
    )
    assert response.status_code in (401, 403)