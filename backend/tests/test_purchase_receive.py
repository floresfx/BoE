"""Tests de recepción de mercancía."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from app.models import (
    PurchaseRequest,
    PurchaseRequestLine,
    Resource,
    Warehouse,
)


@pytest.fixture
def warehouse(db: Session, tenant) -> Warehouse:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    w = Warehouse(name="Bodega Test", code="WH-TEST", is_active=True)
    db.add(w)
    db.flush()
    return w


@pytest.fixture
def receive_resource(db: Session, tenant, unit) -> Resource:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    r = Resource(
        name="Recurso Receive Test",
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
def approved_request(
    db: Session, tenant, receive_resource
) -> PurchaseRequest:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    req = PurchaseRequest(
        code="REQ-RECV-001",
        status="approved",
        needed_by=None,
        notes="Test recepción",
    )
    db.add(req)
    db.flush()
    db.add(
        PurchaseRequestLine(
            request_id=req.id,
            resource_id=receive_resource.id,
            quantity=Decimal("100.0"),
            quantity_received=Decimal("0"),
        )
    )
    db.flush()
    db.refresh(req)
    return req


def test_receive_full(
    client: TestClient,
    auth_headers,
    approved_request,
    warehouse,
    receive_resource,
):
    """Recepción completa: 100/100."""
    lines = approved_request.lines
    response = client.post(
        f"/api/v1/purchase-requests/{approved_request.id}/receive",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse.id),
            "lines": [
                {
                    "line_id": str(lines[0].id),
                    "received_quantity": "100.0",
                    "lot_code": "LOT-RECV-001",
                    "unit_cost": "10.0",
                }
            ],
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["new_status"] == "completed"
    assert len(data["lines"]) == 1

    # Verificar stock
    stock = client.get(
        "/api/v1/stock/consolidated", headers=auth_headers
    )
    items = stock.json()["items"]
    found = next(
        (s for s in items if s["resource_id"] == str(receive_resource.id)),
        None,
    )
    assert found is not None
    assert float(found["total_quantity"]) == 100.0


def test_receive_partial(
    client: TestClient,
    auth_headers,
    approved_request,
    warehouse,
):
    """Recepción parcial: 60/100."""
    lines = approved_request.lines
    response = client.post(
        f"/api/v1/purchase-requests/{approved_request.id}/receive",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse.id),
            "lines": [
                {
                    "line_id": str(lines[0].id),
                    "received_quantity": "60.0",
                    "lot_code": "LOT-RECV-002",
                }
            ],
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["new_status"] == "partially_received"


def test_receive_multiple_times(
    client: TestClient,
    auth_headers,
    approved_request,
    warehouse,
):
    """Recibir 60, luego 40 → completed."""
    lines = approved_request.lines

    r1 = client.post(
        f"/api/v1/purchase-requests/{approved_request.id}/receive",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse.id),
            "lines": [
                {
                    "line_id": str(lines[0].id),
                    "received_quantity": "60.0",
                    "lot_code": "LOT-A",
                }
            ],
        },
    )
    assert r1.status_code == 201, r1.json()
    assert r1.json()["new_status"] == "partially_received"

    r2 = client.post(
        f"/api/v1/purchase-requests/{approved_request.id}/receive",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse.id),
            "lines": [
                {
                    "line_id": str(lines[0].id),
                    "received_quantity": "40.0",
                    "lot_code": "LOT-B",
                }
            ],
        },
    )
    assert r2.status_code == 201, r2.json()
    assert r2.json()["new_status"] == "completed"


def test_receive_mas_de_lo_pendiente_falla(
    client: TestClient,
    auth_headers,
    approved_request,
    warehouse,
):
    """Recibir más de lo pendiente → 400."""
    lines = approved_request.lines
    response = client.post(
        f"/api/v1/purchase-requests/{approved_request.id}/receive",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse.id),
            "lines": [
                {
                    "line_id": str(lines[0].id),
                    "received_quantity": "150.0",
                    "lot_code": "LOT-X",
                }
            ],
        },
    )
    assert response.status_code == 400


def test_receive_solicitud_no_aprobada_falla(
    client: TestClient,
    auth_headers,
    warehouse,
    receive_resource,
    db: Session,
    tenant,
):
    """Recibir una solicitud no aprobada → 400."""
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    req = PurchaseRequest(code="REQ-NOT-APPROVED", status="draft")
    db.add(req)
    db.flush()
    line = PurchaseRequestLine(
        request_id=req.id,
        resource_id=receive_resource.id,
        quantity=Decimal("10.0"),
        quantity_received=Decimal("0"),
    )
    db.add(line)
    db.flush()

    response = client.post(
        f"/api/v1/purchase-requests/{req.id}/receive",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse.id),
            "lines": [
                {
                    "line_id": str(line.id),
                    "received_quantity": "10.0",
                    "lot_code": "LOT-Y",
                }
            ],
        },
    )
    assert response.status_code == 400