from uuid import uuid4

from fastapi.testclient import TestClient

from app.models import Plan


def test_create_plan(client: TestClient, auth_headers: dict):
    """Crear un plan (requiere auth)."""
    name = f"Plan Test {uuid4().hex[:6]}"
    response = client.post(
        "/api/v1/plans",
        headers=auth_headers,
        json={
            "name": name,
            "description": "Test",
            "price": 39.00,
            "currency": "USD",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == name


def test_list_plans(client: TestClient, auth_headers: dict, plan: Plan):
    """Listar planes."""
    response = client.get("/api/v1/plans", headers=auth_headers)
    assert response.status_code == 200
    assert any(p["id"] == str(plan.id) for p in response.json())


def test_update_plan(client: TestClient, auth_headers: dict, plan: Plan):
    """Actualizar un plan."""
    response = client.put(
        f"/api/v1/plans/{plan.id}",
        headers=auth_headers,
        json={"price": 49.00},
    )
    assert response.status_code == 200
    assert float(response.json()["price"]) == 49.00