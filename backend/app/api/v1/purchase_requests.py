"""CRUD de Purchase Requests (por tenant)."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_tenant
from app.api.permissions import require_permission
from app.core.database import get_db
from app.models import (
    PurchaseRequest,
    PurchaseRequestLine,
    PURCHASE_REQUEST_STATUSES,
    Resource,
    Supplier,
    Tenant,
)
from app.schemas.purchase_request import (
    PurchaseRequestCreate,
    PurchaseRequestFromBundleRequest,
    PurchaseRequestLineResponse,
    PurchaseRequestListResponse,
    PurchaseRequestResponse,
    PurchaseRequestStatusUpdate,
    PurchaseRequestUpdate,
)
from app.services.bundle_service import explode_bundle

router = APIRouter(prefix="/purchase-requests", tags=["purchase-requests"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_tenant_schema(db: Session, tenant: Tenant) -> None:
    """Fuerza el search_path al schema del tenant (defensa en profundidad)."""
    db.execute(text(f'SET LOCAL search_path TO "{tenant.schema_name}", public'))


def _get_or_404(
    db: Session, request_id: UUID, tenant: Tenant
) -> PurchaseRequest:
    """Busca una solicitud en el schema del tenant actual (filtrado explícito)."""
    from sqlalchemy import text

    # Query explícita al schema del tenant (sin depender del search_path)
    result = db.execute(
        text(
            f'SELECT id FROM "{tenant.schema_name}".purchase_requests '
            f'WHERE id = :request_id'
        ),
        {"request_id": str(request_id)},
    ).scalar()

    if result is None:
        raise HTTPException(404, "Solicitud no encontrada")

    # Ahora cargar el objeto completo
    r = (
        db.query(PurchaseRequest)
        .options(joinedload(PurchaseRequest.lines))
        .filter(PurchaseRequest.id == request_id)
        .first()
    )
    if not r:
        raise HTTPException(404, "Solicitud no encontrada")
    return r


def _build_line_response(
    db: Session, line: PurchaseRequestLine
) -> PurchaseRequestLineResponse:
    resource = db.query(Resource).filter(Resource.id == line.resource_id).first()
    supplier = (
        db.query(Supplier).filter(Supplier.id == line.supplier_id).first()
        if line.supplier_id
        else None
    )
    return PurchaseRequestLineResponse(
        id=line.id,
        resource_id=line.resource_id,
        resource_name=resource.name if resource else "",
        quantity=line.quantity,
        supplier_id=line.supplier_id,
        supplier_name=supplier.name if supplier else None,
        notes=line.notes,
    )


def _build_response(db: Session, req: PurchaseRequest) -> PurchaseRequestResponse:
    return PurchaseRequestResponse(
        id=req.id,
        code=req.code,
        status=req.status,
        needed_by=req.needed_by,
        notes=req.notes,
        created_at=req.created_at,
        updated_at=req.updated_at,
        lines=[_build_line_response(db, l) for l in req.lines],
    )


def _generate_code(db: Session) -> str:
    """Genera un código único tipo REQ-2026-001."""
    from datetime import datetime

    year = datetime.now().year
    prefix = f"REQ-{year}-"
    last = (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.code.like(f"{prefix}%"))
        .order_by(PurchaseRequest.code.desc())
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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=PurchaseRequestListResponse)
def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    _set_tenant_schema(db, current_tenant)
    query = db.query(PurchaseRequest).options(joinedload(PurchaseRequest.lines))
    if status_filter:
        query = query.filter(PurchaseRequest.status == status_filter)
    if search:
        query = query.filter(PurchaseRequest.code.ilike(f"%{search}%"))
    total = query.count()
    items = (
        query.order_by(PurchaseRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return PurchaseRequestListResponse(
        items=[_build_response(db, r) for r in items],
        total=total,
    )


@router.get("/{request_id}", response_model=PurchaseRequestResponse)
def get_request(
    request_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    r = _get_or_404(db, request_id, current_tenant)
    return _build_response(db, r)


@router.post(
    "",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("purchase_request", "crear"))],
)
def create_request(
    data: PurchaseRequestCreate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    _set_tenant_schema(db, current_tenant)
    existing = (
        db.query(PurchaseRequest).filter(PurchaseRequest.code == data.code).first()
    )
    if existing:
        raise HTTPException(400, "Ya existe una solicitud con ese código")

    req_data = data.model_dump(exclude={"lines"})
    req = PurchaseRequest(**req_data, status="draft")
    db.add(req)
    db.flush()

    for line in data.lines:
        resource = db.query(Resource).filter(Resource.id == line.resource_id).first()
        if not resource:
            raise HTTPException(
                400, f"Recurso no encontrado: {line.resource_id}"
            )
        if line.supplier_id:
            supplier = (
                db.query(Supplier).filter(Supplier.id == line.supplier_id).first()
            )
            if not supplier:
                raise HTTPException(
                    400, f"Proveedor no encontrado: {line.supplier_id}"
                )
        db.add(
            PurchaseRequestLine(
                request_id=req.id,
                resource_id=line.resource_id,
                quantity=line.quantity,
                supplier_id=line.supplier_id,
                notes=line.notes,
            )
        )

    db.flush()
    db.refresh(req)
    req = _get_or_404(db, req.id, current_tenant)
    return _build_response(db, req)


@router.post(
    "/from-bundle",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_from_bundle(
    data: PurchaseRequestFromBundleRequest,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Crea una solicitud a partir de un bundle explotado.

    Cada componente del bundle se convierte en una línea de la solicitud.
    """
    _set_tenant_schema(db, current_tenant)
    exploded = explode_bundle(db, data.bundle_id, data.multiplier)

    code = data.code or _generate_code(db)
    existing = db.query(PurchaseRequest).filter(PurchaseRequest.code == code).first()
    if existing:
        raise HTTPException(400, "Ya existe una solicitud con ese código")

    req = PurchaseRequest(
        code=code,
        status="draft",
        needed_by=data.needed_by,
        notes=data.notes or f"Generada desde bundle {exploded['bundle_code']}",
    )
    db.add(req)
    db.flush()

    for comp in exploded["components"]:
        db.add(
            PurchaseRequestLine(
                request_id=req.id,
                resource_id=comp["resource_id"],
                quantity=comp["required_quantity"],
                supplier_id=None,
                notes=comp["notes"],
            )
        )

    db.flush()
    db.refresh(req)
    req = _get_or_404(db, req.id, current_tenant)
    return _build_response(db, req)


# ---------------------------------------------------------------------------
# Update genérico (sin cambiar status)
# ---------------------------------------------------------------------------

@router.put(
    "/{request_id}",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission("purchase_request", "editar"))],
)
def update_request(
    request_id: UUID,
    data: PurchaseRequestUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza los datos generales de la solicitud (sin cambiar status)."""
    req = _get_or_404(db, request_id, current_tenant)
    if req.status not in ("draft", "pending"):
        raise HTTPException(
            400, f"No se puede editar una solicitud en estado {req.status}"
        )
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(req, key, value)
    db.flush()
    db.refresh(req)
    req = _get_or_404(db, request_id, current_tenant)
    return _build_response(db, req)


# ---------------------------------------------------------------------------
# Cambio de status
# ---------------------------------------------------------------------------

@router.put(
    "/{request_id}/status",
    response_model=PurchaseRequestResponse,
    dependencies=[Depends(require_permission("purchase_request", "aprobar"))],
)
def update_status(
    request_id: UUID,
    data: PurchaseRequestStatusUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Cambia el estado de la solicitud."""
    if data.status not in PURCHASE_REQUEST_STATUSES:
        raise HTTPException(400, f"Estado inválido: {data.status}")
    req = _get_or_404(db, request_id, current_tenant)
    req.status = data.status
    db.flush()
    db.refresh(req)
    req = _get_or_404(db, request_id, current_tenant)
    return _build_response(db, req)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Solo se pueden borrar solicitudes en borrador."""
    req = _get_or_404(db, request_id, current_tenant)
    if req.status != "draft":
        raise HTTPException(400, "Solo se pueden borrar solicitudes en borrador")
    db.delete(req)
    db.flush()


# ---------------------------------------------------------------------------
# Líneas de la solicitud
# ---------------------------------------------------------------------------

@router.post(
    "/{request_id}/lines",
    response_model=PurchaseRequestLineResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_line(
    request_id: UUID,
    data: dict,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Añade una línea a la solicitud."""
    from uuid import UUID as UUIDType

    _set_tenant_schema(db, current_tenant)
    req = _get_or_404(db, request_id, current_tenant)
    if req.status not in ("draft", "pending"):
        raise HTTPException(400, "La solicitud no acepta cambios en su estado actual")

    resource_id = data.get("resource_id")
    quantity = data.get("quantity")
    if not resource_id or quantity is None:
        raise HTTPException(400, "resource_id y quantity son requeridos")

    try:
        resource_uuid = UUIDType(resource_id)
        quantity_decimal = Decimal(str(quantity))
    except (ValueError, TypeError):
        raise HTTPException(400, "Datos inválidos")

    resource = db.query(Resource).filter(Resource.id == resource_uuid).first()
    if not resource:
        raise HTTPException(400, "Recurso no encontrado")

    existing = (
        db.query(PurchaseRequestLine)
        .filter(
            PurchaseRequestLine.request_id == request_id,
            PurchaseRequestLine.resource_id == resource_uuid,
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "El recurso ya está en la solicitud")

    line = PurchaseRequestLine(
        request_id=request_id,
        resource_id=resource_uuid,
        quantity=quantity_decimal,
        supplier_id=data.get("supplier_id"),
        notes=data.get("notes"),
    )
    db.add(line)
    db.flush()
    db.refresh(line)
    return _build_line_response(db, line)


@router.delete(
    "/{request_id}/lines/{line_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_line(
    request_id: UUID,
    line_id: UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    _set_tenant_schema(db, current_tenant)
    req = _get_or_404(db, request_id, current_tenant)
    if req.status not in ("draft", "pending"):
        raise HTTPException(400, "La solicitud no acepta cambios en su estado actual")
    line = (
        db.query(PurchaseRequestLine)
        .filter(
            PurchaseRequestLine.id == line_id,
            PurchaseRequestLine.request_id == request_id,
        )
        .first()
    )
    if not line:
        raise HTTPException(404, "Línea no encontrada")
    db.delete(line)
    db.flush()