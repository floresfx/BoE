"""Seed de planes."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Currency, Feature, Plan, PlanFeature, PlanLimit


PLANS = [
    {
        "code": "mpr_base",
        "name": "MPR Base",
        "price": "39.00",
        "currency_code": "USD",
        "interval": "monthly",
        "trial_days": 14,
        "features": [
            "inventario",
            "planificacion",
            "anexos",
            "excepciones",
            "costeo_basico",
            "ia_basica",
            "exportacion",
            "importacion",
            "notificaciones",
        ],
        "limits": {
            "paquetes": 10,
            "recursos": 50,
            "usuarios": 3,
        },
    },
    {
        "code": "mpr_plus",
        "name": "MPR Plus",
        "price": "79.00",
        "currency_code": "USD",
        "interval": "monthly",
        "trial_days": 14,
        "features": [
            "inventario",
            "planificacion",
            "anexos",
            "excepciones",
            "costeo_completo",
            "ia_completa",
            "exportacion",
            "importacion",
            "notificaciones",
            "marketplace",
            "multi_moneda",
            "multi_usuario",
        ],
        "limits": {
            "paquetes": None,
            "recursos": None,
            "usuarios": 10,
        },
    },
    {
        "code": "mp_gratuito",
        "name": "Marketplace Gratuito",
        "price": "0.00",
        "currency_code": "USD",
        "interval": "monthly",
        "trial_days": 0,
        "features": [
            "marketplace",
            "notificaciones",
        ],
        "limits": {
            "productos": 10,
            "ventas_mes": 3,
            "leads_mes": 3,
        },
    },
    {
        "code": "mp_basico",
        "name": "Marketplace Basico",
        "price": "19.00",
        "currency_code": "USD",
        "interval": "monthly",
        "trial_days": 0,
        "features": [
            "marketplace",
            "notificaciones",
            "exportacion",
        ],
        "limits": {
            "productos": 100,
            "ventas_mes": 20,
            "leads_mes": 10,
        },
    },
    {
        "code": "mp_plus",
        "name": "Marketplace Plus",
        "price": "35.00",
        "currency_code": "USD",
        "interval": "monthly",
        "trial_days": 0,
        "features": [
            "marketplace",
            "notificaciones",
            "exportacion",
            "importacion",
            "insignias",
            "permisos_normas",
        ],
        "limits": {
            "productos": None,
            "ventas_mes": 40,
            "leads_mes": 30,
        },
    },
]


def seed_plans(db: Session) -> int:
    """Crea los planes iniciales con sus features y limites. Idempotente."""
    count = 0

    currencies = {c.code: c for c in db.query(Currency).all()}
    features = {f.code: f for f in db.query(Feature).all()}

    for data in PLANS:
        existing = (
            db.query(Plan).filter(Plan.code == data["code"]).first()
        )
        if existing:
            continue

        currency = currencies.get(data["currency_code"])
        if not currency:
            raise ValueError(f"Moneda no encontrada: {data['currency_code']}")

        plan = Plan(
            code=data["code"],
            name=data["name"],
            price=Decimal(data["price"]),
            currency_id=currency.id,
            interval=data["interval"],
            trial_days=data["trial_days"],
        )
        db.add(plan)
        db.flush()

        # Añadir features
        for feature_code in data["features"]:
            feature = features.get(feature_code)
            if not feature:
                raise ValueError(f"Feature no encontrada: {feature_code}")
            db.add(PlanFeature(plan_id=plan.id, feature_id=feature.id))

        # Añadir limits
        for limit_code, value in data["limits"].items():
            db.add(
                PlanLimit(
                    plan_id=plan.id,
                    limit_code=limit_code,
                    value=value,
                )
            )

        count += 1

    db.commit()
    return count