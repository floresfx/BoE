"""Tests del módulo Purchase Requests."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Bundle,
    BundleComponent,
    PurchaseRequest,
    PurchaseRequestLine,
    Resource,
)


@pytest.fixture
def pr_resource(db: Session, tenant, unit) -> Resource:
    from sqlalchemy import text as sql_text
    db.execute(sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    r = Resource(
        name="Recurso PR Test",
        resource_type="materia_prima",
        base_unit_id=unit.id,
        cost=Decimal("10.00"),
        waste_percent=Decimal("0"),
        is_active=True,
    )
    db.add(r)
    db.flush()
    return r


@pytest.fixture
def pr_bundle(db: Session, tenant, pr_resource) -> Bundle:
    from sqlalchemy import text as sql_text
    db.execute(sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    b = Bundle(code="BUN-PR-TEST", name="Bundle PR", is_active=True)
    db.add(b)
    db.flush()
    db.add(
        BundleComponent(
            bundle_id=b.id, resource_id=pr_resource.id, quantity=Decimal("5.0")
        )
    )
    db.flush()
    return b


def test_create_purchase_request(client: TestClient, auth_headers, pr_resource):
    response = client.post(
        "/api/v1/purchase-requests",
        headers=auth_headers,
        json={
            "code": "REQ-TEST-001",
            "needed_by": None,
            "notes": "Test",
            "lines": [
                {
                    "resource_id": str(pr_resource.id),
                    "quantity": "10.0",
                }
            ],
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["code"] == "REQ-TEST-001"
    assert data["status"] == "draft"
    assert len(data["lines"]) == 1


def test_create_purchase_request_code_duplicado(
    client: TestClient, auth_headers, pr_resource
):
    payload = {
        "code": "REQ-DUP",
        "lines": [
            {"resource_id": str(pr_resource.id), "quantity": "5.0"}
        ],
    }
    r1 = client.post(
        "/api/v1/purchase-requests", headers=auth_headers, json=payload
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/api/v1/purchase-requests", headers=auth_headers, json=payload
    )
    assert r2.status_code == 400


def test_create_purchase_request_from_bundle(
    client: TestClient, auth_headers, pr_bundle
):
    response = client.post(
        "/api/v1/purchase-requests/from-bundle",
        headers=auth_headers,
        json={
            "bundle_id": str(pr_bundle.id),
            "multiplier": "2.0",
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    # Bundle tiene 1 componente, quantity 5 * multiplier 2 = 10
    assert len(data["lines"]) == 1
    assert float(data["lines"][0]["quantity"]) == 10.0


def test_update_purchase_request_status(
    client: TestClient, auth_headers, pr_resource
):
    # Crear
    created = client.post(
        "/api/v1/purchase-requests",
        headers=auth_headers,
        json={
            "code": "REQ-STATUS",
            "lines": [
                {"resource_id": str(pr_resource.id), "quantity": "5.0"}
            ],
        },
    ).json()

    # Cambiar a pending
    response = client.put(
        f"/api/v1/purchase-requests/{created['id']}/status",
        headers=auth_headers,
        json={"status": "pending"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


def test_update_purchase_request_invalid_status(
    client: TestClient, auth_headers, pr_resource
):
    created = client.post(
        "/api/v1/purchase-requests",
        headers=auth_headers,
        json={
            "code": "REQ-BAD-STATUS",
            "lines": [
                {"resource_id": str(pr_resource.id), "quantity": "5.0"}
            ],
        },
    ).json()

    response = client.put(
        f"/api/v1/purchase-requests/{created['id']}/status",
        headers=auth_headers,
        json={"status": "invalid_status"},
    )
    # 400 si el endpoint valida, 422 si Pydantic valida. Ambos son válidos.
    assert response.status_code in (400, 422), (
        f"Esperado 400 o 422, recibido {response.status_code}: {response.json()}"
    )


def test_delete_purchase_request_solo_draft(
    client: TestClient, auth_headers, pr_resource
):
    created = client.post(
        "/api/v1/purchase-requests",
        headers=auth_headers,
        json={
            "code": "REQ-DEL",
            "lines": [
                {"resource_id": str(pr_resource.id), "quantity": "5.0"}
            ],
        },
    ).json()

    # Cambiar a pending
    client.put(
        f"/api/v1/purchase-requests/{created['id']}/status",
        headers=auth_headers,
        json={"status": "pending"},
    )

    # Intentar borrar → 400
    response = client.delete(
        f"/api/v1/purchase-requests/{created['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_purchase_requests_aislados_por_tenant(
    client: TestClient,
    auth_headers,
    pr_resource,
    tenant_factory,
    user_factory,
    token_for_user,
):
    """Verifica que un tenant no puede acceder a las solicitudes de otro."""
    # Crear en tenant A
    created_a = client.post(
        "/api/v1/purchase-requests",
        headers=auth_headers,
        json={
            "code": "REQ-ISO-A",
            "lines": [
                {"resource_id": str(pr_resource.id), "quantity": "5.0"}
            ],
        },
    )
    assert created_a.status_code == 201
    req_a_id = created_a.json()["id"]

    # Crear otro tenant
    other_tenant = tenant_factory(name="Other Tenant")
    other_user, _ = user_factory(other_tenant)
    other_token = token_for_user(other_user)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Intentar acceder al ID de la solicitud del tenant A desde el tenant B
    # Debe devolver 404 porque la solicitud no existe en el schema del tenant B
    response = client.get(
        f"/api/v1/purchase-requests/{req_a_id}", headers=other_headers
    )
    assert response.status_code == 404, (
        f"FUGA: tenant B puede acceder a solicitud del tenant A. "
        f"Response: {response.status_code} - {response.json()}"
    )