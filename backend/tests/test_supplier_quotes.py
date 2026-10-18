"""Tests de envío a proveedores y cotizaciones (Bloque 6.2.a)."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from app.models import (
    PurchaseRequest,
    PurchaseRequestLine,
    Resource,
    Supplier,
)


@pytest.fixture
def quote_supplier(db: Session, tenant) -> Supplier:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    s = Supplier(
        code="SUP-QUOTE", name="Proveedor Quote", is_active=True
    )
    db.add(s)
    db.flush()
    return s


@pytest.fixture
def quote_supplier_2(db: Session, tenant) -> Supplier:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    s = Supplier(
        code="SUP-QUOTE-2", name="Proveedor Quote 2", is_active=True
    )
    db.add(s)
    db.flush()
    return s


@pytest.fixture
def quote_resource(db: Session, tenant, unit) -> Resource:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    r = Resource(
        name="Recurso Quote Test",
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
def draft_request(db: Session, tenant, quote_resource) -> PurchaseRequest:
    db.execute(
        sql_text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    req = PurchaseRequest(code="REQ-QUOTE-001", status="draft")
    db.add(req)
    db.flush()
    db.add(
        PurchaseRequestLine(
            request_id=req.id,
            resource_id=quote_resource.id,
            quantity=Decimal("100.0"),
            quantity_received=Decimal("0"),
        )
    )
    db.flush()
    db.refresh(req)
    return req


# --- Tests ---

def test_send_request_to_suppliers(
    client: TestClient, auth_headers, draft_request
):
    """Enviar solicitud: draft → pending."""
    response = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["status"] == "pending"


def test_send_request_ya_enviada_falla(
    client: TestClient, auth_headers, draft_request
):
    """Enviar una solicitud ya enviada → 400."""
    # Primera vez: OK
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    # Segunda vez: 400
    response = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_create_quote(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
):
    """Crear una cotización para una línea."""
    # Enviar primero
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )

    line = draft_request.lines[0]
    response = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json={
            "line_id": str(line.id),
            "supplier_id": str(quote_supplier.id),
            "unit_price": "9.50",
            "currency_code": "USD",
            "lead_time_days": 5,
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()
    assert float(data["unit_price"]) == 9.50
    assert data["status"] == "pending"
    assert data["supplier_name"] == "Proveedor Quote"


def test_create_quote_duplicada_falla(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
):
    """Misma cotización dos veces → 400."""
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    line = draft_request.lines[0]

    payload = {
        "line_id": str(line.id),
        "supplier_id": str(quote_supplier.id),
        "unit_price": "9.50",
        "lead_time_days": 5,
    }
    # Primera: OK
    r1 = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json=payload,
    )
    assert r1.status_code == 201

    # Segunda: 400
    r2 = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json=payload,
    )
    assert r2.status_code == 400


def test_create_quote_solicitud_draft_falla(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
):
    """Cotizar una solicitud en 'draft' → 400."""
    line = draft_request.lines[0]
    response = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json={
            "line_id": str(line.id),
            "supplier_id": str(quote_supplier.id),
            "unit_price": "9.50",
            "lead_time_days": 5,
        },
    )
    assert response.status_code == 400


def test_list_quotes(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
    quote_supplier_2,
):
    """Listar cotizaciones de una solicitud."""
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    line = draft_request.lines[0]

    # Crear 2 cotizaciones (2 proveedores)
    for supplier, price in [
        (quote_supplier, "9.50"),
        (quote_supplier_2, "9.00"),
    ]:
        client.post(
            f"/api/v1/purchase-requests/{draft_request.id}/quotes",
            headers=auth_headers,
            json={
                "line_id": str(line.id),
                "supplier_id": str(supplier.id),
                "unit_price": price,
                "lead_time_days": 5,
            },
        )

    response = client.get(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    # Ordenadas por precio
    assert float(data["items"][0]["unit_price"]) == 9.00
    assert float(data["items"][1]["unit_price"]) == 9.50

# --- Tests de actualización, eliminación y selección ---

def test_update_quote(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
):
    """Actualizar una cotización pending."""
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    line = draft_request.lines[0]

    created = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json={
            "line_id": str(line.id),
            "supplier_id": str(quote_supplier.id),
            "unit_price": "9.50",
            "lead_time_days": 5,
        },
    ).json()

    response = client.put(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes/{created['id']}",
        headers=auth_headers,
        json={"unit_price": "9.00", "lead_time_days": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert float(data["unit_price"]) == 9.00
    assert data["lead_time_days"] == 3


def test_update_quote_accepted_falla(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
):
    """Actualizar una cotización ya aceptada → 400."""
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    line = draft_request.lines[0]

    created = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json={
            "line_id": str(line.id),
            "supplier_id": str(quote_supplier.id),
            "unit_price": "9.50",
            "lead_time_days": 5,
        },
    ).json()

    # Seleccionar
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes/{created['id']}/select",
        headers=auth_headers,
    )

    # Intentar actualizar → 400
    response = client.put(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes/{created['id']}",
        headers=auth_headers,
        json={"unit_price": "8.00"},
    )
    assert response.status_code == 400


def test_delete_quote(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
):
    """Eliminar una cotización pending."""
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    line = draft_request.lines[0]

    created = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json={
            "line_id": str(line.id),
            "supplier_id": str(quote_supplier.id),
            "unit_price": "9.50",
            "lead_time_days": 5,
        },
    ).json()

    response = client.delete(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes/{created['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    # Verificar que ya no aparece
    quotes = client.get(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
    )
    assert quotes.json()["total"] == 0


def test_select_quote(
    client: TestClient,
    auth_headers,
    draft_request,
    quote_supplier,
    quote_supplier_2,
):
    """Seleccionar una cotización marca las demás como rejected."""
    client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/send",
        headers=auth_headers,
    )
    line = draft_request.lines[0]

    # Crear 2 cotizaciones
    q1 = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json={
            "line_id": str(line.id),
            "supplier_id": str(quote_supplier.id),
            "unit_price": "9.50",
            "lead_time_days": 5,
        },
    ).json()
    q2 = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
        json={
            "line_id": str(line.id),
            "supplier_id": str(quote_supplier_2.id),
            "unit_price": "9.00",
            "lead_time_days": 7,
        },
    ).json()

    # Seleccionar q1 (más cara pero mejor lead time)
    response = client.post(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes/{q1['id']}/select",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["is_selected"] is True

    # Verificar que q2 está rejected
    quotes = client.get(
        f"/api/v1/purchase-requests/{draft_request.id}/quotes",
        headers=auth_headers,
    ).json()
    for item in quotes["items"]:
        if item["id"] == q2["id"]:
            assert item["status"] == "rejected"
            assert item["is_selected"] is False