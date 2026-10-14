"""Servicio de validación de límites por plan.

Proporciona funciones para verificar que un tenant no exceda los
límites definidos en su plan (plan_limits).

Uso típico en un endpoint:

    from app.services.plan_service import check_plan_limit

    @router.post("/resources")
    def create_resource(...):
        check_plan_limit(db, current_tenant, "recursos", Resource)
        # ... crear recurso
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Plan, PlanLimit, Tenant


def _get_plan_limit(
    db: Session, tenant: Tenant, limit_code: str
) -> int | None:
    """Obtiene el valor del límite para el plan del tenant.

    Devuelve None si:
    - El tenant no tiene plan asignado.
    - El plan no define ese límite.
    - El límite está definido como NULL (ilimitado).
    """
    if not tenant.plan_id:
        return None

    limit = (
        db.query(PlanLimit)
        .filter(
            PlanLimit.plan_id == tenant.plan_id,
            PlanLimit.limit_code == limit_code,
        )
        .first()
    )

    if not limit:
        return None

    return limit.value  # puede ser None (ilimitado)


def check_plan_limit(
    db: Session,
    tenant: Tenant,
    limit_code: str,
    model,
) -> None:
    """Verifica que el tenant no exceda el límite de su plan.

    Args:
        db: sesión SQLAlchemy (con search_path del tenant).
        tenant: tenant actual.
        limit_code: código del límite (ej: "recursos", "paquetes").
        model: modelo SQLAlchemy a contar (ej: Resource, Bundle).

    Raises:
        HTTPException 403: si el límite se excede.
    """
    limit_value = _get_plan_limit(db, tenant, limit_code)

    # Si no hay límite definido o es NULL → sin restricción
    if limit_value is None:
        return

    # Contar los recursos actuales del tenant (vía search_path)
    current_count = db.query(model).count()

    if current_count >= limit_value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Has alcanzado el límite de tu plan "
                f"({limit_value} {limit_code}). "
                f"Actualiza tu plan para continuar."
            ),
        )