"""Tests del módulo de producción (MPS)."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Bundle, BundleComponent, ProductionOrder, ProductionPlan, Resource


@pytest.fixture
def prod_bundle(db: Session, tenant, unit) -> Bundle:
    db.execute(text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    r = Resource(
        name="Recurso Prod",
        resource_type="materia_prima",
        base_unit_id=unit.id,
        cost=Decimal("10.00"),
        waste_percent=Decimal("0"),
        is_active=True,
    )
    db.add(r)
    db.flush()

    b = Bundle(code="BUN-PROD", name="Pan Test", is_active=True)
    db.add(b)
    db.flush()
    db.add(BundleComponent(bundle_id=b.id, resource_id=r.id, quantity=Decimal("2.0")))
    db.flush()
    return b


def test_create_plan(client: TestClient, auth_headers):
    response = client.post(
        "/api/v1/production/plans",
        headers=auth_headers,
        json={"code": "PLAN-001", "name": "Plan Semanal"},
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["code"] == "PLAN-001"
    assert data["status"] == "draft"


def test_create_order(client: TestClient, auth_headers, prod_bundle):
    response = client.post(
        "/api/v1/production/orders",
        headers=auth_headers,
        json={
            "code": "PROD-001",
            "bundle_id": str(prod_bundle.id),
            "quantity": "10.0",
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["code"] == "PROD-001"
    assert data["status"] == "draft"
    assert data["bundle_name"] == "Pan Test"


def test_start_order(client: TestClient, auth_headers, prod_bundle):
    created = client.post(
        "/api/v1/production/orders",
        headers=auth_headers,
        json={
            "code": "PROD-START",
            "bundle_id": str(prod_bundle.id),
            "quantity": "5.0",
        },
    ).json()

    response = client.post(
        f"/api/v1/production/orders/{created['id']}/start",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_complete_order(client: TestClient, auth_headers, prod_bundle):
    created = client.post(
        "/api/v1/production/orders",
        headers=auth_headers,
        json={
            "code": "PROD-COMPLETE",
            "bundle_id": str(prod_bundle.id),
            "quantity": "5.0",
        },
    ).json()

    # Start
    client.post(
        f"/api/v1/production/orders/{created['id']}/start",
        headers=auth_headers,
    )

    # Complete
    response = client.post(
        f"/api/v1/production/orders/{created['id']}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"