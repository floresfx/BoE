from fastapi.testclient import TestClient

from app.models import Permission, Role, Tenant


def test_create_role(client: TestClient, tenant: Tenant):
    """Test: crear un rol."""
    from uuid import uuid4

    unique_name = f"TestRole_{uuid4().hex[:8]}"
    response = client.post(
        "/api/v1/roles",
        json={
            "tenant_id": str(tenant.id),
            "name": unique_name,
            "description": "Administrador",
            "permission_ids": [],
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["name"] == unique_name


def test_create_role_con_permisos(
    client: TestClient, tenant: Tenant, permission: Permission
):
    """Test: crear rol con permisos."""
    response = client.post(
        "/api/v1/roles",
        json={
            "tenant_id": str(tenant.id),
            "name": "Editor",
            "description": "Editor",
            "permission_ids": [str(permission.id)],
        },
    )
    assert response.status_code == 201


def test_list_roles(client: TestClient, tenant: Tenant):
    """Test: listar roles."""
    response = client.get(f"/api/v1/roles?tenant_id={tenant.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_role(client: TestClient, tenant: Tenant):
    """Test: actualizar rol."""
    # Crear rol primero
    create_response = client.post(
        "/api/v1/roles",
        json={
            "tenant_id": str(tenant.id),
            "name": "Lector",
            "description": "Lector",
            "permission_ids": [],
        },
    )
    role_id = create_response.json()["id"]

    # Actualizar
    response = client.put(
        f"/api/v1/roles/{role_id}",
        json={"description": "Lector actualizado"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Lector actualizado"