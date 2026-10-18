"""Servicio de recepción de mercancía."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    PurchaseRequest,
    PurchaseRequestLine,
    Resource,
    Tenant,
    Warehouse,
)
from app.schemas.purchase_request_receive import (
    ReceiveLineResponse,
    ReceiveRequest,
    ReceiveResponse,
)
from app.services.inventory_service import register_movement


def receive_purchase_request(
    db: Session,
    tenant: Tenant,
    request_id: UUID,
    data: ReceiveRequest,
) -> ReceiveResponse:
    """
    Recibe mercancía de una solicitud aprobada.

    - Crea movimientos `in` de inventario.
    - Actualiza `quantity_received` en cada línea.
    - Cambia el estado de la solicitud a `completed` o `partially_received`.
    """
    # Forzar search_path al schema del tenant
    db.execute(
        text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )

    # 1. Validar solicitud
    req = (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(404, "Solicitud no encontrada")

    if req.status not in ("approved", "partially_received"):
        raise HTTPException(
            400,
            f"Solo se pueden recibir solicitudes en estado 'approved' o "
            f"'partially_received'. Estado actual: {req.status}",
        )

    # 2. Validar warehouse
    warehouse = (
        db.query(Warehouse)
        .filter(Warehouse.id == data.warehouse_id)
        .first()
    )
    if not warehouse:
        raise HTTPException(404, "Warehouse no encontrado")

    # 3. Procesar cada línea recibida
    lines_by_id = {line.id: line for line in req.lines}
    received_responses: list[ReceiveLineResponse] = []

    for line_in in data.lines:
        line = lines_by_id.get(line_in.line_id)
        if not line:
            raise HTTPException(
                400,
                f"Línea {line_in.line_id} no pertenece a esta solicitud",
            )

        # Validar que no se reciba más de lo pendiente
        pending = line.quantity - (line.quantity_received or Decimal("0"))
        if line_in.received_quantity > pending:
            raise HTTPException(
                400,
                f"Línea {line.id}: recibes {line_in.received_quantity} "
                f"pero solo quedan {pending} por recibir",
            )

        # Crear movimiento `in`
        movement = register_movement(
            db=db,
            warehouse_id=data.warehouse_id,
            resource_id=line.resource_id,
            lot_code=line_in.lot_code,
            movement_type="in",
            quantity=line_in.received_quantity,
            unit_cost=line_in.unit_cost,
            expiration=line_in.expiration,
            reference=req.code,
            notes=line_in.notes,
            created_by=None,
        )

        # Actualizar cantidad recibida en la línea
        line.quantity_received = (
            line.quantity_received or Decimal("0")
        ) + line_in.received_quantity

        received_responses.append(
            ReceiveLineResponse(
                line_id=line.id,
                resource_id=line.resource_id,
                resource_name="",  # se llena abajo
                quantity_received=line_in.received_quantity,
                lot_code=line_in.lot_code,
                movement_id=movement.id,
            )
        )

    # 4. Determinar nuevo estado
    all_received = all(
        (l.quantity_received or Decimal("0")) >= l.quantity
        for l in req.lines
    )

    new_status = "completed" if all_received else "partially_received"
    req.status = new_status

    if data.notes:
        req.notes = (req.notes or "") + f"\nRecepción: {data.notes}"

    db.flush()

    # 5. Cargar nombres de recursos para la respuesta
    for resp in received_responses:
        resource = (
            db.query(Resource)
            .filter(Resource.id == resp.resource_id)
            .first()
        )
        if resource:
            resp.resource_name = resource.name

    total_requested = sum(l.quantity for l in req.lines)
    total_received = sum(
        l.quantity_received or Decimal("0") for l in req.lines
    )

    return ReceiveResponse(
        request_id=req.id,
        request_code=req.code,
        new_status=new_status,
        lines=received_responses,
        message=(
            f"Recepción {'completa' if all_received else 'parcial'}. "
            f"Recibido: {total_received} de {total_requested}."
        ),
    )