from fastapi.testclient import TestClient

from app.models import Permission


def test_list_permissions(
    client: TestClient,
    auth_headers: dict,
    permission: Permission,
):
    """Listar permisos (requiere auth)."""
    response = client.get("/api/v1/permissions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(p["id"] == str(permission.id) for p in data)


def test_list_permissions_por_modulo(
    client: TestClient,
    auth_headers: dict,
    permission: Permission,
):
    """Listar permisos filtrados por módulo."""
    response = client.get(
        f"/api/v1/permissions?module={permission.module}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(p["module"] == permission.module for p in data)
    assert any(p["id"] == str(permission.id) for p in data)