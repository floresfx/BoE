from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Tenant, Vertical


def test_create_tenant(client: TestClient, vertical: Vertical):
    """Test: crear un tenant."""
    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "Clínica San José",
            "tax_id": "J-12345678-9",
            "tax_id_type": "RIF",
            "admin_email": "admin@clinica.com",
            "vertical_id": str(vertical.id),
            "timezone": "America/Caracas",
            "country": "Venezuela",
            "province": "Miranda",
            "city": "Caracas",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Clínica San José"
    assert data["tax_id"] == "J-12345678-9"


def test_create_tenant_tax_id_duplicado(
    client: TestClient, tenant: Tenant, vertical: Vertical
):
    """Test: crear tenant con tax_id duplicado."""
    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "Otro Tenant",
            "tax_id": tenant.tax_id,
            "tax_id_type": "RIF",
            "admin_email": "admin@otro.com",
            "vertical_id": str(vertical.id),
            "country": "Venezuela",
        },
    )
    assert response.status_code == 400


def test_list_tenants(client: TestClient, tenant: Tenant):
    """Test: listar tenants."""
    response = client.get("/api/v1/tenants")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_get_tenant(client: TestClient, tenant: Tenant):
    """Test: obtener tenant por ID."""
    response = client.get(f"/api/v1/tenants/{tenant.id}")
    assert response.status_code == 200
    assert response.json()["name"] == tenant.name


def test_update_tenant(client: TestClient, tenant: Tenant):
    """Test: actualizar tenant."""
    response = client.put(
        f"/api/v1/tenants/{tenant.id}",
        json={"name": "Clínica Actualizada"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Clínica Actualizada"