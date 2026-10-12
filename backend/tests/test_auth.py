from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


def test_login_exitoso(client: TestClient, user: User):
    """Login con credenciales correctas."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user.email


def test_login_password_incorrecta(client: TestClient, user: User):
    """Login con password incorrecta."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]


def test_login_email_no_existe(client: TestClient):
    """Login con email que no existe."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "noexiste@test.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_login_usuario_inactivo(client: TestClient, user: User, db: Session):
    """Login con usuario inactivo → 403."""
    user.status = "inactivo"
    db.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    assert response.status_code == 403


def test_get_me(client: TestClient, auth_headers: dict, user: User):
    """Obtener usuario actual."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_get_me_sin_token(client: TestClient):
    """Obtener usuario actual sin token → 401 (HTTPBearer)."""
    response = client.get("/api/v1/auth/me")
    # HTTPBearer en FastAPI 0.143 devuelve 401 sin credenciales
    assert response.status_code == 401