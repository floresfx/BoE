"""Tests del endpoint POST /register.

Verifica:
1. Registro exitoso (crea tenant + schema + user + asigna rol Admin).
2. Validaciones:
   - Email duplicado → 400
   - Tax ID duplicado → 400
   - Vertical inválido → 400
   - País inválido → 400
3. Login funciona con el user recién creado.
4. Schema del tenant se crea en PostgreSQL.
5. Tablas operativas se crean dentro del schema.
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


def _register_payload(vertical_id: str, **overrides) -> dict:
    """Devuelve un payload de registro válido con overrides."""
    uid = uuid4().hex[:6]
    base = {
        "company_name": f"Test Company {uid}",
        "tax_id": f"J-{uid.upper()}-9",
        "tax_id_type": "RIF",
        "vertical_id": vertical_id,
        "country_code": "VE",
        "admin_email": f"admin_{uid}@test.com",
        "admin_password": "password123",
        "admin_first_name": "Admin",
        "admin_last_name": "Test",
        "admin_phone": "04141234567",
    }
    base.update(overrides)
    return base


def test_register_exitoso(
    client: TestClient, vertical, cleanup_register_schemas
):
    """Registrar un tenant + admin user exitosamente."""
    payload = _register_payload(str(vertical.id))
    response = client.post("/api/v1/register", json=payload)

    assert response.status_code == 201, response.json()
    data = response.json()

    assert "tenant_id" in data
    assert "user_id" in data
    assert data["email"] == payload["admin_email"]
    assert data["schema_name"].startswith("tenant_")
    assert "Registro exitoso" in data["message"]

    cleanup_register_schemas.append(data["schema_name"])


def test_register_email_duplicado(
    client: TestClient, vertical, cleanup_register_schemas
):
    """Email duplicado → 400."""
    email = f"admin_{uuid4().hex[:6]}@test.com"

    # Primer registro
    payload1 = _register_payload(str(vertical.id), admin_email=email)
    r1 = client.post("/api/v1/register", json=payload1)
    assert r1.status_code == 201, r1.json()
    cleanup_register_schemas.append(r1.json()["schema_name"])

    # Segundo registro con el mismo email
    payload2 = _register_payload(str(vertical.id), admin_email=email)
    r2 = client.post("/api/v1/register", json=payload2)
    assert r2.status_code == 400
    assert "email" in r2.json()["detail"].lower()


def test_register_tax_id_duplicado(
    client: TestClient, vertical, cleanup_register_schemas
):
    """Tax ID duplicado → 400."""
    tax_id = f"J-{uuid4().hex[:8].upper()}-9"

    payload1 = _register_payload(str(vertical.id), tax_id=tax_id)
    r1 = client.post("/api/v1/register", json=payload1)
    assert r1.status_code == 201, r1.json()
    cleanup_register_schemas.append(r1.json()["schema_name"])

    payload2 = _register_payload(str(vertical.id), tax_id=tax_id)
    r2 = client.post("/api/v1/register", json=payload2)
    assert r2.status_code == 400
    assert "tax_id" in r2.json()["detail"].lower()


def test_register_vertical_invalido(client: TestClient):
    """Vertical que no existe → 400."""
    payload = _register_payload(str(uuid4()))
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 400
    assert "vertical" in response.json()["detail"].lower()


def test_register_pais_invalido(client: TestClient, vertical):
    """País que no existe → 400."""
    payload = _register_payload(str(vertical.id), country_code="ZZ")
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 400
    assert "país" in response.json()["detail"].lower() or "pais" in response.json()["detail"].lower()


def test_register_crea_schema_y_tablas(
    client: TestClient, vertical, db: Session, cleanup_register_schemas
):
    """El registro crea el schema + tablas operativas en PostgreSQL."""
    payload = _register_payload(str(vertical.id))
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 201, response.json()

    schema_name = response.json()["schema_name"]
    cleanup_register_schemas.append(schema_name)

    # Verificar que el schema existe
    result = db.execute(
        text(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name = :schema"
        ),
        {"schema": schema_name},
    ).first()
    assert result is not None, f"Schema {schema_name} no existe"

    # Verificar que las tablas operativas existen
    for table in ["resources", "resources_attributes", "resources_taxes"]:
        result = db.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = :schema AND table_name = :table"
            ),
            {"schema": schema_name, "table": table},
        ).first()
        assert result is not None, (
            f"Tabla {schema_name}.{table} no existe"
        )


def test_register_luego_login(
    client: TestClient, vertical, cleanup_register_schemas
):
    """Después de registrarse, el user puede hacer login."""
    payload = _register_payload(str(vertical.id))
    r_register = client.post("/api/v1/register", json=payload)
    assert r_register.status_code == 201, r_register.json()

    cleanup_register_schemas.append(r_register.json()["schema_name"])

    # Login
    r_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["admin_email"],
            "password": payload["admin_password"],
        },
    )
    assert r_login.status_code == 200, r_login.json()
    data = r_login.json()
    assert "access_token" in data
    assert data["user"]["email"] == payload["admin_email"]