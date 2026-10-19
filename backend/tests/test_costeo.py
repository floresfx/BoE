"""Tests de costeo FIFO/LIFO."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    Movement,
    Resource,
    StockLot,
    Tenant,
    Warehouse,
)


@pytest.fixture
def costing_warehouse(db: Session, tenant) -> Warehouse:
    db.execute(text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    w = Warehouse(name="Bodega Costeo", code="WH-COST", is_active=True)
    db.add(w)
    db.flush()
    return w


@pytest.fixture
def costing_resource(db: Session, tenant, unit) -> Resource:
    db.execute(text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))
    r = Resource(
        name="Recurso Costeo",
        resource_type="materia_prima",
        base_unit_id=unit.id,
        cost=Decimal("10.00"),
        waste_percent=Decimal("0"),
        is_active=True,
    )
    db.add(r)
    db.flush()
    return r


def test_movement_in_creates_lot(
    client: TestClient,
    auth_headers,
    costing_warehouse,
    costing_resource,
):
    """Un movimiento 'in' crea un lote con el costo unitario indicado."""
    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-FIFO-1",
            "movement_type": "in",
            "quantity": "100.0",
            "unit_cost": "5.0",
        },
    )
    assert response.status_code == 201, response.json()

    # Verificar lote
    lots = client.get(
        f"/api/v1/stock/consolidated?resource_id={costing_resource.id}",
        headers=auth_headers,
    )
    assert lots.status_code == 200


def test_fifo_out_calcula_costo(
    client: TestClient,
    auth_headers,
    costing_warehouse,
    costing_resource,
    tenant,
    db: Session,
):
    """FIFO: el primer lote en entrar es el primero en salir."""
    # Cambiar método a FIFO
    tenant.inventory_costing_method = "fifo"
    db.flush()

    # In 1: 50 unidades a $5
    client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-A",
            "movement_type": "in",
            "quantity": "50.0",
            "unit_cost": "5.0",
        },
    )
    # In 2: 50 unidades a $10
    client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-B",
            "movement_type": "in",
            "quantity": "50.0",
            "unit_cost": "10.0",
        },
    )

    # Out: 60 unidades (debe consumir 50 de LOT-A a $5 + 10 de LOT-B a $10)
    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-OUT",
            "movement_type": "out",
            "quantity": "60.0",
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    # Costo total esperado: 50*5 + 10*10 = 350
    # Costo unitario promedio: 350/60 = 5.8333
    assert float(data["unit_cost"]) == pytest.approx(5.8333, abs=0.01)

    # Verificar reporte de costeo
    report = client.get(
        "/api/v1/inventory/costing/report",
        headers=auth_headers,
    )
    assert report.status_code == 200
    rep_data = report.json()
    assert rep_data["method"] == "fifo"
    assert float(rep_data["total_cost"]) == pytest.approx(350.0, abs=0.01)


def test_lifo_out_calcula_costo(
    client: TestClient,
    auth_headers,
    costing_warehouse,
    costing_resource,
    tenant,
    db: Session,
):
    """LIFO: el último lote en entrar es el primero en salir."""
    tenant.inventory_costing_method = "lifo"
    db.flush()

    # In 1: 50 unidades a $5
    client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-A",
            "movement_type": "in",
            "quantity": "50.0",
            "unit_cost": "5.0",
        },
    )
    # In 2: 50 unidades a $10
    client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-B",
            "movement_type": "in",
            "quantity": "50.0",
            "unit_cost": "10.0",
        },
    )

    # Out: 60 unidades (debe consumir 50 de LOT-B a $10 + 10 de LOT-A a $5)
    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-OUT",
            "movement_type": "out",
            "quantity": "60.0",
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    # Costo total esperado: 50*10 + 10*5 = 550
    # Costo unitario promedio: 550/60 = 9.1667
    assert float(data["unit_cost"]) == pytest.approx(9.1667, abs=0.01)

    # Verificar reporte de costeo
    report = client.get(
        "/api/v1/inventory/costing/report",
        headers=auth_headers,
    )
    assert report.status_code == 200
    rep_data = report.json()
    assert rep_data["method"] == "lifo"
    assert float(rep_data["total_cost"]) == pytest.approx(550.0, abs=0.01)


def test_out_sin_stock_falla(
    client: TestClient,
    auth_headers,
    costing_warehouse,
    costing_resource,
):
    """Un 'out' sin stock suficiente devuelve 400."""
    response = client.post(
        "/api/v1/movements",
        headers=auth_headers,
        json={
            "warehouse_id": str(costing_warehouse.id),
            "resource_id": str(costing_resource.id),
            "lot_code": "LOT-EMPTY",
            "movement_type": "out",
            "quantity": "10.0",
        },
    )
    assert response.status_code == 400