from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Tenant, User


def test_create_user(
    client: TestClient,
    auth_headers: dict,
    tenant: Tenant,
):
    """Crear un user en el tenant autenticado."""
    email = f"new-{uuid4().hex[:8]}@test.com"
    response = client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "email": email,
            "password": "password123",
            "first_name": "Nuevo",
            "last_name": "User",
            "phone": "04121112233",
            "phone_verified": False,
            "status": "activo",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["tenant_id"] == str(tenant.id)
    assert data["status"] == "activo"


def test_create_user_email_duplicado(
    client: TestClient,
    auth_headers: dict,
    user: User,
):
    """Crear user con email ya existente → 400."""
    response = client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "email": user.email,
            "password": "password123",
            "first_name": "X",
            "last_name": "Y",
        },
    )
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_list_users(
    client: TestClient,
    auth_headers: dict,
    user: User,
):
    """Listar users del tenant autenticado."""
    response = client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == user.email


def test_list_users_por_tenant(
    client: TestClient,
    tenant_factory,
    user_factory,
    token_for_user,
):
    """Un user de A no ve users de B."""
    tenant_a = tenant_factory(name="A")
    tenant_b = tenant_factory(name="B")
    user_a, _ = user_factory(tenant_a)
    user_b, _ = user_factory(tenant_b)

    token_a = token_for_user(user_a)
    token_b = token_for_user(user_b)

    r_a = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token_a}"}
    )
    r_b = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token_b}"}
    )

    assert r_a.status_code == 200
    assert r_b.status_code == 200
    assert r_a.json()["total"] == 1
    assert r_b.json()["total"] == 1
    assert r_a.json()["items"][0]["email"] == user_a.email
    assert r_b.json()["items"][0]["email"] == user_b.email


def test_get_user(
    client: TestClient,
    auth_headers: dict,
    user: User,
):
    """Obtener un user del tenant autenticado."""
    response = client.get(f"/api/v1/users/{user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_update_user(
    client: TestClient,
    auth_headers: dict,
    user: User,
):
    """Actualizar un user del tenant autenticado."""
    response = client.put(
        f"/api/v1/users/{user.id}",
        headers=auth_headers,
        json={"first_name": "Actualizado"},
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Actualizado"