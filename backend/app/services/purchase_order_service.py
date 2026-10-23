"""Servicio de órdenes de compra."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseRequest,
    PurchaseRequestLine,
    Resource,
    Supplier,
    SupplierQuote,
    Tenant,
    Warehouse,
)
from app.schemas.purchase_order import (
    PurchaseOrderLineResponse,
    PurchaseOrderResponse,
)
from app.services.inventory_service import register_movement


def _set_tenant_schema(db: Session, tenant: Tenant) -> None:
    db.execute(text(f'SET search_path TO "{tenant.schema_name}", public'))


def _reset_search_path(db: Session) -> None:
    db.execute(text('SET search_path TO public'))


def _generate_order_code(db: Session) -> str:
    year = datetime.now().year
    prefix = f"PO-{year}-"
    last = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.code.like(f"{prefix}%"))
        .order_by(PurchaseOrder.code.desc())
        .first()
    )
    if last:
        try:
            num = int(last.code.replace(prefix, "")) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"{prefix}{num:04d}"


def _build_response(db: Session, order: PurchaseOrder) -> PurchaseOrderResponse:
    supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
    lines = []
    for line in order.lines:
        resource = db.query(Resource).filter(Resource.id == line.resource_id).first()
        lines.append(
            PurchaseOrderLineResponse(
                id=line.id,
                resource_id=line.resource_id,
                resource_name=resource.name if resource else "",
                quantity=line.quantity,
                unit_price=line.unit_price,
                subtotal=line.subtotal,
            )
        )
    return PurchaseOrderResponse(
        id=order.id,
        code=order.code,
        request_id=order.request_id,
        supplier_id=order.supplier_id,
        supplier_name=supplier.name if supplier else "",
        status=order.status,
        total=order.total,
        currency_code=order.currency_code,
        expected_delivery=order.expected_delivery,
        notes=order.notes,
        lines=lines,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def generate_order_from_quote(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
    quote_id: UUID,
) -> PurchaseOrderResponse:
    """Genera una orden de compra desde una cotización aceptada."""
    _set_tenant_schema(db, tenant)

    # 1. Validar solicitud
    req = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not req:
        _reset_search_path(db)
        raise HTTPException(404, "Solicitud no encontrada")

    # 2. Validar cotización
    quote = db.query(SupplierQuote).filter(SupplierQuote.id == quote_id).first()
    if not quote:
        _reset_search_path(db)
        raise HTTPException(404, "Cotización no encontrada")

    if quote.request_id != request_id:
        _reset_search_path(db)
        raise HTTPException(400, "La cotización no pertenece a esta solicitud")

    if quote.status != "accepted":
        _reset_search_path(db)
        raise HTTPException(400, "Solo se puede generar orden desde una cotización aceptada")

    # 3. Crear orden
    code = _generate_order_code(db)
    order = PurchaseOrder(
        code=code,
        request_id=request_id,
        supplier_id=quote.supplier_id,
        status="draft",
        total=Decimal("0"),
        currency_code=quote.currency_code,
        notes=f"Generada desde cotización {quote.id}",
    )
    db.add(order)
    db.flush()

    # 4. Crear línea
    line = PurchaseOrderLine(
        order_id=order.id,
        resource_id=(
            db.query(PurchaseRequestLine)
            .filter(PurchaseRequestLine.id == quote.line_id)
            .first()
            .resource_id
        ),
        quantity=(
            db.query(PurchaseRequestLine)
            .filter(PurchaseRequestLine.id == quote.line_id)
            .first()
            .quantity
        ),
        unit_price=quote.unit_price,
        subtotal=quote.unit_price * (
            db.query(PurchaseRequestLine)
            .filter(PurchaseRequestLine.id == quote.line_id)
            .first()
            .quantity
        ),
    )
    db.add(line)
    db.flush()

    # 5. Actualizar total
    order.total = line.subtotal
    db.flush()
    db.refresh(order)

    _reset_search_path(db)
    return _build_response(db, order)


def confirm_order(
    db: Session,
    tenant: Tenant,
    order_id: UUID,
) -> PurchaseOrderResponse:
    """Confirma una orden de compra."""
    _set_tenant_schema(db, tenant)

    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        _reset_search_path(db)
        raise HTTPException(404, "Orden no encontrada")

    if order.status != "draft":
        _reset_search_path(db)
        raise HTTPException(400, f"No se puede confirmar una orden en estado {order.status}")

    order.status = "confirmed"
    db.flush()
    db.refresh(order)
    response = _build_response(db, order)

    _reset_search_path(db)
    return response


def receive_order(
    db: Session,
    tenant: Tenant,
    order_id: UUID,
    warehouse_id: UUID,
) -> PurchaseOrderResponse:
    """Recibe la mercancía de una orden de compra."""
    _set_tenant_schema(db, tenant)

    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        _reset_search_path(db)
        raise HTTPException(404, "Orden no encontrada")

    if order.status != "confirmed":
        _reset_search_path(db)
        raise HTTPException(400, f"No se puede recibir una orden en estado {order.status}")

    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        _reset_search_path(db)
        raise HTTPException(404, "Warehouse no encontrado")

    # Crear movimientos `in` por cada línea
    for line in order.lines:
        register_movement(
            db=db,
            warehouse_id=warehouse_id,
            resource_id=line.resource_id,
            lot_code=f"PO-{order.code}-{line.id.hex[:6]}",
            movement_type="in",
            quantity=line.quantity,
            unit_cost=line.unit_price,
            expiration=None,
            reference=order.code,
            notes=f"Recepción de orden {order.code}",
            created_by=None,
        )

    order.status = "received"
    db.flush()
    db.refresh(order)
    response = _build_response(db, order)

    _reset_search_path(db)
    return response


def list_orders(
    db: Session,
    tenant: Tenant,
) -> list[PurchaseOrderResponse]:
    """Lista todas las órdenes de compra."""
    _set_tenant_schema(db, tenant)
    orders = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).all()
    responses = [_build_response(db, o) for o in orders]
    _reset_search_path(db)
    return responses