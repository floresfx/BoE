"""Servicio de cotizaciones de proveedores."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    PurchaseRequest,
    PurchaseRequestLine,
    Supplier,
    SupplierQuote,
    Tenant,
)


def _set_tenant_schema(db: Session, tenant: Tenant) -> None:
    """Fuerza el search_path al schema del tenant."""
    db.execute(
        text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )


def send_request_to_suppliers(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
) -> PurchaseRequest:
    """Cambia el estado de la solicitud de 'draft' a 'pending'.

    Esto indica que la solicitud fue enviada a proveedores.
    """
    _set_tenant_schema(db, tenant)

    req = (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(404, "Solicitud no encontrada")

    if req.status != "draft":
        raise HTTPException(
            400,
            f"Solo se pueden enviar solicitudes en estado 'draft'. "
            f"Estado actual: {req.status}",
        )

    req.status = "pending"
    db.flush()
    db.refresh(req)
    return req


def create_quote(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
    line_id: UUID,
    supplier_id: UUID,
    unit_price: Decimal,
    currency_code: str,
    lead_time_days: int,
    valid_until,
    notes: str | None,
) -> SupplierQuote:
    """Crea una cotización para una línea de una solicitud."""
    _set_tenant_schema(db, tenant)

    # 1. Validar solicitud
    req = (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(404, "Solicitud no encontrada")

    if req.status not in ("pending", "quoted"):
        raise HTTPException(
            400,
            f"Solo se pueden cotizar solicitudes en estado 'pending' o "
            f"'quoted'. Estado actual: {req.status}",
        )

    # 2. Validar línea
    line = (
        db.query(PurchaseRequestLine)
        .filter(
            PurchaseRequestLine.id == line_id,
            PurchaseRequestLine.request_id == request_id,
        )
        .first()
    )
    if not line:
        raise HTTPException(
            400, "La línea no pertenece a esta solicitud"
        )

    # 3. Validar proveedor
    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id)
        .first()
    )
    if not supplier:
        raise HTTPException(404, "Proveedor no encontrado")

    # 4. Validar que no exista ya una cotización de este proveedor
    #    para esta línea
    existing = (
        db.query(SupplierQuote)
        .filter(
            SupplierQuote.line_id == line_id,
            SupplierQuote.supplier_id == supplier_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            400,
            "Ya existe una cotización de este proveedor para esta línea",
        )

    # 5. Crear la cotización
    quote = SupplierQuote(
        request_id=request_id,
        line_id=line_id,
        supplier_id=supplier_id,
        unit_price=unit_price,
        currency_code=currency_code,
        lead_time_days=lead_time_days,
        valid_until=valid_until,
        notes=notes,
        status="pending",
        is_selected=False,
    )
    db.add(quote)
    db.flush()
    db.refresh(quote)

    # 6. Si la solicitud estaba en 'pending', cambiar a 'quoted'
    if req.status == "pending":
        req.status = "quoted"
        db.flush()

    return quote


def list_quotes(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
) -> list[SupplierQuote]:
    """Lista todas las cotizaciones de una solicitud."""
    _set_tenant_schema(db, tenant)

    req = (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(404, "Solicitud no encontrada")

    quotes = (
        db.query(SupplierQuote)
        .filter(SupplierQuote.request_id == request_id)
        .order_by(
            SupplierQuote.line_id,
            SupplierQuote.unit_price.asc(),
        )
        .all()
    )
    return quotes

def update_quote(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
    quote_id: UUID,
    unit_price: Decimal | None = None,
    currency_code: str | None = None,
    lead_time_days: int | None = None,
    valid_until=None,
    notes: str | None = None,
) -> SupplierQuote:
    """Actualiza una cotización (solo si está pending)."""
    _set_tenant_schema(db, tenant)

    quote = (
        db.query(SupplierQuote)
        .filter(
            SupplierQuote.id == quote_id,
            SupplierQuote.request_id == request_id,
        )
        .first()
    )
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")

    if quote.status != "pending":
        raise HTTPException(
            400,
            f"Solo se pueden editar cotizaciones en estado 'pending'. "
            f"Estado actual: {quote.status}",
        )

    if unit_price is not None:
        quote.unit_price = unit_price
    if currency_code is not None:
        quote.currency_code = currency_code
    if lead_time_days is not None:
        quote.lead_time_days = lead_time_days
    if valid_until is not None:
        quote.valid_until = valid_until
    if notes is not None:
        quote.notes = notes

    db.flush()
    db.refresh(quote)
    return quote


def delete_quote(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
    quote_id: UUID,
) -> None:
    """Elimina una cotización (solo si está pending)."""
    _set_tenant_schema(db, tenant)

    quote = (
        db.query(SupplierQuote)
        .filter(
            SupplierQuote.id == quote_id,
            SupplierQuote.request_id == request_id,
        )
        .first()
    )
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")

    if quote.status != "pending":
        raise HTTPException(
            400,
            f"Solo se pueden eliminar cotizaciones en estado 'pending'. "
            f"Estado actual: {quote.status}",
        )

    db.delete(quote)
    db.flush()


def select_quote(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
    quote_id: UUID,
) -> SupplierQuote:
    """Marca una cotización como elegida.

    - La cotización elegida pasa a `accepted`.
    - Las demás cotizaciones de la misma línea pasan a `rejected`.
    - `is_selected = True` en la elegida.
    """
    _set_tenant_schema(db, tenant)

    quote = (
        db.query(SupplierQuote)
        .filter(
            SupplierQuote.id == quote_id,
            SupplierQuote.request_id == request_id,
        )
        .first()
    )
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")

    if quote.status != "pending":
        raise HTTPException(
            400,
            f"Solo se pueden seleccionar cotizaciones en estado 'pending'. "
            f"Estado actual: {quote.status}",
        )

    # Marcar todas las cotizaciones de la misma línea como rejected
    siblings = (
        db.query(SupplierQuote)
        .filter(
            SupplierQuote.line_id == quote.line_id,
            SupplierQuote.id != quote.id,
        )
        .all()
    )
    for sibling in siblings:
        sibling.status = "rejected"
        sibling.is_selected = False

    # Marcar la elegida como accepted
    quote.status = "accepted"
    quote.is_selected = True

    db.flush()
    db.refresh(quote)
    return quote