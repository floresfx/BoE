from uuid import uuid4

from fastapi.testclient import TestClient

from app.models import Vertical


def test_list_verticals_vacio(client: TestClient):
    """Listar verticals es público (para signup)."""
    response = client.get("/api/v1/verticals")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_vertical(client: TestClient, auth_headers: dict):
    """Crear un vertical requiere auth."""
    uid = uuid4().hex
    response = client.post(
        "/api/v1/verticals",
        headers=auth_headers,
        json={
            "code": f"test_vertical_{uid[:8]}",
            "name": f"Vertical Test {uid[:8]}",
            "description": "Test",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"].startswith("test_vertical_")


def test_get_vertical(client: TestClient, vertical: Vertical):
    """Obtener vertical por ID es público."""
    response = client.get(f"/api/v1/verticals/{vertical.id}")
    assert response.status_code == 200
    assert response.json()["name"] == vertical.name


def test_get_vertical_no_existe(client: TestClient):
    """Vertical inexistente devuelve 404."""
    from uuid import uuid4
    response = client.get(f"/api/v1/verticals/{uuid4()}")
    assert response.status_code == 404


def test_update_vertical(
    client: TestClient, auth_headers: dict, vertical: Vertical
):
    """Actualizar vertical requiere auth."""
    response = client.put(
        f"/api/v1/verticals/{vertical.id}",
        headers=auth_headers,
        json={"description": "Actualizado"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Actualizado"