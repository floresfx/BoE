from uuid import uuid4

from fastapi.testclient import TestClient

from app.models import Profile


def test_create_profile(client: TestClient, auth_headers: dict):
    """Crear un perfil (requiere auth)."""
    name = f"Perfil Test {uuid4().hex[:6]}"
    response = client.post(
        "/api/v1/profiles",
        headers=auth_headers,
        json={"name": name, "description": "Test"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == name


def test_list_profiles(client: TestClient, auth_headers: dict, profile: Profile):
    """Listar perfiles."""
    response = client.get("/api/v1/profiles", headers=auth_headers)
    assert response.status_code == 200
    assert any(p["id"] == str(profile.id) for p in response.json())


def test_update_profile(
    client: TestClient, auth_headers: dict, profile: Profile
):
    """Actualizar un perfil."""
    response = client.put(
        f"/api/v1/profiles/{profile.id}",
        headers=auth_headers,
        json={"description": "Actualizado"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Actualizado"