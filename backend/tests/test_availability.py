# tests/test_availability.py
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Resource, Bundle, BundleComponent, StockLot, Supplier, SupplierResource


def test_check_availability_covered(client: TestClient, auth_headers: dict, resource: Resource, stock_lot: StockLot, tenant, db: Session):
    """Test: el stock es suficiente para cubrir la solicitud."""
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))
    response = client.post(
        "/api/v1/availability/check",
        headers=auth_headers,
        json={"resource_id": str(resource.id), "quantity": 3.0},
    )
    db.execute(text('SET search_path TO public'))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "covered"
    assert float(data["missing_quantity"]) == 0.0
    assert len(data["suppliers"]) == 0


def test_check_availability_partial(client: TestClient, auth_headers: dict, resource: Resource, stock_lot: StockLot, supplier_with_offer: Supplier, tenant, db: Session):
    """Test: el stock es parcial, debe sugerir proveedores."""
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))
    response = client.post(
        "/api/v1/availability/check",
        headers=auth_headers,
        json={"resource_id": str(resource.id), "quantity": 20.0},
    )
    db.execute(text('SET search_path TO public'))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "partial"
    assert float(data["missing_quantity"]) == 15.0
    assert len(data["suppliers"]) > 0
    assert data["suppliers"][0]["supplier_name"] == supplier_with_offer.name


def test_check_availability_out_of_stock(client: TestClient, auth_headers: dict, resource: Resource, supplier_with_offer: Supplier, tenant, db: Session):
    """Test: no hay stock, debe devolver out_of_stock y sugerir proveedores."""
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))
    response = client.post(
        "/api/v1/availability/check",
        headers=auth_headers,
        json={"resource_id": str(resource.id), "quantity": 10.0},
    )
    db.execute(text('SET search_path TO public'))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "out_of_stock"
    assert float(data["available_quantity"]) == 0.0
    assert len(data["suppliers"]) > 0


# --- Tests para un Bundle ---

@pytest.fixture
def bundle_with_components(db: Session, tenant, resource: Resource) -> Bundle:
    """Fixture para un bundle con un componente."""
    from uuid import uuid4 as _uuid4

    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))

    uid = _uuid4().hex[:6]
    bundle = Bundle(
        code=f"BUN-{uid}",
        name=f"Test Bundle {uid}",
        is_active=True,
    )
    db.add(bundle)
    db.flush()
    db.add(BundleComponent(bundle_id=bundle.id, resource_id=resource.id, quantity=2))
    db.flush()
    db.refresh(bundle)

    db.execute(text('SET search_path TO public'))
    return bundle


def test_check_bundle_partial(client: TestClient, auth_headers: dict, bundle_with_components: Bundle, stock_lot: StockLot, supplier_with_offer: Supplier, tenant, db: Session):
    """Test: verificar un bundle con un componente parcial."""
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))
    response = client.post(
        "/api/v1/availability/check-bundle",
        headers=auth_headers,
        json={"bundle_id": str(bundle_with_components.id), "multiplier": 10.0},
    )
    db.execute(text('SET search_path TO public'))
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "partial"
    assert data["lines"][0]["status"] == "partial"
    assert len(data["lines"][0]["suppliers"]) > 0


def test_check_bundle_tenant_isolation(client: TestClient, auth_headers: dict, bundle_with_components: Bundle, stock_lot_from_other_tenant: StockLot, tenant, db: Session):
    """Test: el stock de otro tenant no debe afectar el cálculo."""
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))
    response = client.post(
        "/api/v1/availability/check-bundle",
        headers=auth_headers,
        json={"bundle_id": str(bundle_with_components.id), "multiplier": 1.0},
    )
    db.execute(text('SET search_path TO public'))
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "out_of_stock"