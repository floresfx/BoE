"""Tests del módulo Inventory (warehouses, stock_lots, movements)."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Movement,
    Resource,
    StockLot,
    Warehouse,
)


# --- Fixtures ---

@pytest.fixture
def warehouse_a(db: Session, tenant) -> Warehouse:
    db.execute(__import__("sqlalchemy").text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    w = Warehouse(name="Bodega A", code="WH-A", is_active=True)
    db.add(w)
    db.flush()
    return w


@pytest.fixture
def warehouse_b(db: Session, tenant) -> Warehouse:
    db.execute(__import__("sqlalchemy").text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    w = Warehouse(name="Bodega B", code="WH-B", is_active=True)
    db.add(w)
    db.flush()
    return w


@pytest.fixture
def inventory_resource(db: Session, tenant, unit) -> Resource:
    db.execute(__import__("sqlalchemy").text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    r = Resource(
        name="Recurso Inventory Test",
        resource_type="materia_prima",
        base_unit_id=unit.id,
        cost=Decimal("5.00"),
        waste_percent=Decimal("0"),
        is_active=True,
    )
    db.add(r)
    db.flush()
    return r


# --- Tests Warehouses ---

def test_create_warehouse(client: TestClient, auth_headers, tenant):
    response = client.post(
        "/api/v1/warehouses",
        headers=auth_headers,
        json={"name": "Bodega Nueva", "code": "WH-NEW", "is_active": True},
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["name"] == "Bodega Nueva"
    assert data["code"] == "WH-NEW"


def test_create_warehouse_code_duplicado(
    client: TestClient, auth_headers, warehouse_a
):
    response = client.post(
        "/api/v1/warehouses",
        headers=auth_headers,
        json={"name": "Otra Bodega", "code": "WH-A"},
    )
    assert response.status_code == 400


def test_list_warehouses(client: TestClient, auth_headers, warehouse_a):
    response = client.get("/api/v1/warehouses", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(w["code"] == "WH-A" for w in data["items"])


# --- Tests Movements ---

def test_movement_in_suma_stock(
    client: TestClient, auth_headers, warehouse_a, inventory_resource
):
    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse_a.id),
            "resource_id": str(inventory_resource.id),
            "lot_code": "LOT-IN-001",
            "movement_type": "in",
            "quantity": "100.0",
            "unit_cost": "5.0",
        },
    )
    assert response.status_code == 201, response.json()

    # Verificar stock consolidado
    stock = client.get(
        "/api/v1/stock/consolidated", headers=auth_headers
    )
    assert stock.status_code == 200
    items = stock.json()["items"]
    found = next(
        (s for s in items if s["resource_id"] == str(inventory_resource.id)),
        None,
    )
    assert found is not None
    assert float(found["total_quantity"]) == 100.0


def test_movement_out_resta_stock(
    client: TestClient, auth_headers, warehouse_a, inventory_resource
):
    # Primero: in
    client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse_a.id),
            "resource_id": str(inventory_resource.id),
            "lot_code": "LOT-OUT-001",
            "movement_type": "in",
            "quantity": "100.0",
        },
    )

    # Luego: out
    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse_a.id),
            "resource_id": str(inventory_resource.id),
            "lot_code": "LOT-OUT-001",
            "movement_type": "out",
            "quantity": "30.0",
        },
    )
    assert response.status_code == 201, response.json()

    # Verificar stock = 70
    stock = client.get(
        "/api/v1/stock/consolidated", headers=auth_headers
    )
    items = stock.json()["items"]
    found = next(
        (s for s in items if s["resource_id"] == str(inventory_resource.id)),
        None,
    )
    assert float(found["total_quantity"]) == 70.0


def test_movement_out_mas_que_stock_falla(
    client: TestClient, auth_headers, warehouse_a, inventory_resource
):
    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse_a.id),
            "resource_id": str(inventory_resource.id),
            "lot_code": "LOT-EMPTY",
            "movement_type": "out",
            "quantity": "10.0",
        },
    )
    assert response.status_code == 400


def test_stock_consolidado_por_warehouse(
    client: TestClient,
    auth_headers,
    warehouse_a,
    warehouse_b,
    inventory_resource,
):
    # in en A: 100
    client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse_a.id),
            "resource_id": str(inventory_resource.id),
            "lot_code": "LOT-A",
            "movement_type": "in",
            "quantity": "100.0",
        },
    )
    # in en B: 50
    client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse_b.id),
            "resource_id": str(inventory_resource.id),
            "lot_code": "LOT-B",
            "movement_type": "in",
            "quantity": "50.0",
        },
    )

    stock = client.get(
        "/api/v1/stock/consolidated", headers=auth_headers
    )
    items = stock.json()["items"]
    # Deben aparecer 2 filas (una por warehouse) con el mismo resource_id
    matching = [
        s for s in items if s["resource_id"] == str(inventory_resource.id)
    ]
    assert len(matching) == 2
    total = sum(float(s["total_quantity"]) for s in matching)
    assert total == 150.0


# --- Tests Expiration Alerts ---

def test_expiration_alert_proximo(
    client: TestClient, auth_headers, warehouse_a, inventory_resource, db: Session
):
    from sqlalchemy import text as sql_text

    db.execute(
        sql_text(f'SET LOCAL search_path TO "{warehouse_a.__class__.__module__ and ""}", public')
    ) if False else None

    # Crear lote con caducidad en 10 días
    tenant_schema = db.execute(
        sql_text("SELECT current_schema()")
    ).scalar()

    # Crear movimiento con caducidad cercana
    from datetime import timedelta

    exp_date = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()

    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(warehouse_a.id),
            "resource_id": str(inventory_resource.id),
            "lot_code": "LOT-EXP",
            "movement_type": "in",
            "quantity": "20.0",
            "expiration": exp_date,
        },
    )
    assert response.status_code == 201, response.json()

    # Verificar alerta
    alerts = client.get(
        "/api/v1/stock/expiration-alerts?days_ahead=30",
        headers=auth_headers,
    )
    assert alerts.status_code == 200
    data = alerts.json()
    assert len(data) >= 1
    found = next(
        (a for a in data if a["lot_code"] == "LOT-EXP"), None
    )
    assert found is not None
    assert found["days_until_expiration"] <= 10