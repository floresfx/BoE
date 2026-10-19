import os
import subprocess
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantListResponse,
    TenantResponse,
    TenantUpdate,
    TenantSettingsUpdate,
)
from app.api.deps import get_current_tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_schema_name() -> str:
    """Genera un schema_name seguro y único.

    Formato: tenant_<uuid_hex_32>
    - No editable por el usuario.
    - No visible al usuario.
    - No revela información.
    """
    return f"tenant_{uuid4().hex}"


def _apply_migrations_to_schema(schema_name: str) -> None:
    """Aplica migraciones Alembic al schema del tenant.

    Corre en subproceso para aislar el state de Alembic del proceso web.
    Requiere que alembic/env.py soporte ALEMBIC_TARGET=tenant:<schema>.
    """
    env = os.environ.copy()
    env["ALEMBIC_TARGET"] = f"tenant:{schema_name}"

    # Directorio backend/ (donde está alembic.ini)
    backend_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=backend_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Error aplicando migraciones a {schema_name}: {result.stderr}"
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=TenantListResponse)
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Lista todos los tenants."""
    query = db.query(Tenant)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return TenantListResponse(
        items=[TenantResponse.model_validate(t) for t in items],
        total=total,
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: UUID, db: Session = Depends(get_db)):
    """Obtiene un tenant por ID."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado",
        )
    return TenantResponse.model_validate(tenant)


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db)):
    """Crea un nuevo tenant.

    Pasos:
    1. Validar tax_id único.
    2. Generar schema_name (sistema).
    3. Insertar en public.tenants.
    4. CREATE SCHEMA en Postgres.
    5. Aplicar migraciones operativas al nuevo schema.
    6. Devolver tenant.
    """
    existing = db.query(Tenant).filter(Tenant.tax_id == data.tax_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un tenant con ese tax_id",
        )

    schema_name = _generate_schema_name()

    tenant = Tenant(**data.model_dump(), schema_name=schema_name)
    db.add(tenant)
    db.flush()  # asigna id sin commit

    # Crear el schema en Postgres
    db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
    db.commit()  # commit ANTES de Alembic (abre su propia conexión)

    # Aplicar migraciones al nuevo schema
    if os.getenv("SKIP_TENANT_MIGRATIONS") != "1":
        try:
            _apply_migrations_to_schema(schema_name)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Tenant creado pero migraciones fallaron: {e}",
            )

    db.refresh(tenant)
    return TenantResponse.model_validate(tenant)

@router.put("/settings", response_model=TenantResponse)
def update_settings(
    data: TenantSettingsUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza la configuración del tenant actual.

    - `inventory_costing_method`: 'fifo' | 'lifo'
    """
    if data.inventory_costing_method is not None:
        if data.inventory_costing_method not in ("fifo", "lifo"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Método de costeo inválido. Use 'fifo' o 'lifo'",
            )
        current_tenant.inventory_costing_method = data.inventory_costing_method

    db.commit()
    db.refresh(current_tenant)
    return TenantResponse.model_validate(current_tenant)

@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza un tenant. El schema_name NO es editable."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado",
        )

    update_data = data.model_dump(exclude_unset=True)
    # Blindaje: schema_name nunca se actualiza desde fuera
    update_data.pop("schema_name", None)

    for key, value in update_data.items():
        setattr(tenant, key, value)

    db.commit()
    db.refresh(tenant)
    return TenantResponse.model_validate(tenant)

