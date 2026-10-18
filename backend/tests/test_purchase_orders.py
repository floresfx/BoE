"""Tests de las tablas base del Bloque 6.1."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from app.models import (
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseRequest,
    PurchaseRequestLine,
    Resource,
    Supplier,
    SupplierQuote,
)


@pytest.fixture
def po_supplier(db: Session, tenant) -> Supplier:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    s = Supplier(code="SUP-PO", name="Proveedor PO", is_active=True)
    db.add(s)
    db.flush()
    return s


@pytest.fixture
def po_resource(db: Session, tenant, unit) -> Resource:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    r = Resource(
        name="Recurso PO Test",
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
def po_request(db: Session, tenant, po_resource) -> PurchaseRequest:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    req = PurchaseRequest(code="REQ-PO-001", status="approved")
    db.add(req)
    db.flush()
    db.add(
        PurchaseRequestLine(
            request_id=req.id,
            resource_id=po_resource.id,
            quantity=Decimal("100.0"),
            quantity_received=Decimal("0"),
        )
    )
    db.flush()
    db.refresh(req)
    return req


def test_create_supplier_quote(
    db: Session, tenant, po_request, po_supplier
):
    """Crear una cotización básica."""
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    line = po_request.lines[0]
    quote = SupplierQuote(
        request_id=po_request.id,
        line_id=line.id,
        supplier_id=po_supplier.id,
        unit_price=Decimal("9.50"),
        currency_code="USD",
        lead_time_days=5,
        status="pending",
        is_selected=False,
    )
    db.add(quote)
    db.flush()
    assert quote.id is not None
    assert quote.status == "pending"


def test_create_purchase_order(
    db: Session, tenant, po_request, po_supplier, po_resource
):
    """Crear una orden de compra con una línea."""
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    order = PurchaseOrder(
        code="PO-001",
        request_id=po_request.id,
        supplier_id=po_supplier.id,
        status="draft",
        total=Decimal("950.00"),
        currency_code="USD",
    )
    db.add(order)
    db.flush()

    db.add(
        PurchaseOrderLine(
            order_id=order.id,
            resource_id=po_resource.id,
            quantity=Decimal("100.0"),
            unit_price=Decimal("9.50"),
            subtotal=Decimal("950.00"),
        )
    )
    db.flush()
    db.refresh(order)

    assert order.id is not None
    assert len(order.lines) == 1
    assert float(order.total) == 950.0


def test_purchase_order_statuses():
    """Verificar los estados válidos."""
    from app.models import PURCHASE_ORDER_STATUSES

    assert "draft" in PURCHASE_ORDER_STATUSES
    assert "sent" in PURCHASE_ORDER_STATUSES
    assert "confirmed" in PURCHASE_ORDER_STATUSES
    assert "received" in PURCHASE_ORDER_STATUSES
    assert "completed" in PURCHASE_ORDER_STATUSES
    assert "cancelled" in PURCHASE_ORDER_STATUSES


def test_supplier_quote_multiples_por_linea(
    db: Session, tenant, po_request, po_supplier, po_resource
):
    """Varios proveedores pueden cotizar la misma línea de la solicitud."""
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    line = po_request.lines[0]

    # Crear un segundo proveedor
    supplier2 = Supplier(
        code="SUP-PO-2", name="Proveedor PO 2", is_active=True
    )
    db.add(supplier2)
    db.flush()

    # Crear 2 cotizaciones para la MISMA línea, de 2 proveedores distintos
    for supplier in [po_supplier, supplier2]:
        quote = SupplierQuote(
            request_id=po_request.id,
            line_id=line.id,
            supplier_id=supplier.id,
            unit_price=Decimal("9.00"),
            lead_time_days=3,
        )
        db.add(quote)
    db.flush()

    quotes = (
        db.query(SupplierQuote)
        .filter(SupplierQuote.line_id == line.id)
        .all()
    )
    assert len(quotes) == 2