from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    Tenant,
    TenantActiveAttribute,
    TenantActiveCategory,
    TenantActiveUnit,
    Unit, Category, Attribute, Currency
)
from app.schemas.tenant_settings import (
    TenantSettingsResponse,
    TenantSettingsUpdate,
)

router = APIRouter(prefix="/tenant/settings", tags=["tenant-settings"])


def _get_settings_for_tenant(db: Session, tenant: Tenant) -> TenantSettingsResponse:
    active_units = [au.unit_id for au in tenant.active_units]
    active_categories = [ac.category_id for ac in tenant.active_categories]
    active_attributes = [aa.attribute_id for aa in tenant.active_attributes]

    return TenantSettingsResponse(
        base_currency_id=tenant.base_currency_id,
        inventory_costing_method=tenant.inventory_costing_method,
        active_unit_ids=active_units,
        active_category_ids=active_categories,
        active_attribute_ids=active_attributes,
    )


@router.get("/", response_model=TenantSettingsResponse)
def get_tenant_settings(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Obtiene la configuración de la fundación del tenant actual."""
    return _get_settings_for_tenant(db, current_tenant)


@router.put("/", response_model=TenantSettingsResponse)
def update_tenant_settings(
    data: TenantSettingsUpdate,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Actualiza la configuración de la fundación del tenant."""

    # 1. Actualizar campos simples
    if data.inventory_costing_method is not None:
        if data.inventory_costing_method not in ("fifo", "lifo"):
            raise HTTPException(status_code=400, detail="Método de costeo inválido.")
        current_tenant.inventory_costing_method = data.inventory_costing_method

    if data.base_currency_id is not None:
        currency = db.query(Currency).filter(Currency.id == data.base_currency_id).first()
        if not currency:
            raise HTTPException(status_code=404, detail="Moneda no encontrada.")
        current_tenant.base_currency_id = data.base_currency_id

    # 2. Sincronizar unidades activas
    if data.active_unit_ids is not None:
        db.query(TenantActiveUnit).filter(TenantActiveUnit.tenant_id == current_tenant.id).delete()
        for unit_id in data.active_unit_ids:
            # Opcional: validar que la unidad existe
            db.add(TenantActiveUnit(tenant_id=current_tenant.id, unit_id=unit_id))

    # 3. Sincronizar categorías activas
    if data.active_category_ids is not None:
        db.query(TenantActiveCategory).filter(TenantActiveCategory.tenant_id == current_tenant.id).delete()
        for cat_id in data.active_category_ids:
            db.add(TenantActiveCategory(tenant_id=current_tenant.id, category_id=cat_id))

    # 4. Sincronizar atributos activos
    if data.active_attribute_ids is not None:
        db.query(TenantActiveAttribute).filter(TenantActiveAttribute.tenant_id == current_tenant.id).delete()
        for attr_id in data.active_attribute_ids:
            db.add(TenantActiveAttribute(tenant_id=current_tenant.id, attribute_id=attr_id))

    db.flush()
    db.refresh(current_tenant)
    return _get_settings_for_tenant(db, current_tenant)