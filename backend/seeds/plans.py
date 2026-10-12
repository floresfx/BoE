from sqlalchemy.orm import Session

from app.models import Plan

PLANS = [
    {
        "name": "MPR Base",
        "description": "Plan base del MPR. 10 paquetes, 50 recursos, 3 usuarios.",
        "price": 39.00,
        "currency": "USD",
        "features": {
            "paquetes": 10,
            "recursos": 50,
            "usuarios": 3,
            "inventario": "con lotes y caducidad",
            "planificacion": "calendario + kanban",
            "anexos": True,
            "excepciones": True,
            "costeo": "básico",
            "ia": "básica",
            "soporte": "email",
        },
        "limits": {
            "paquetes": 10,
            "recursos": 50,
            "usuarios": 3,
        },
        "is_active": True,
    },
    {
        "name": "MPR Plus",
        "description": "Plan plus del MPR. Paquetes ilimitados, recursos ilimitados, 10 usuarios.",
        "price": 79.00,
        "currency": "USD",
        "features": {
            "paquetes": "ilimitados",
            "recursos": "ilimitados",
            "usuarios": 10,
            "inventario": "con lotes y caducidad",
            "planificacion": "calendario + kanban",
            "anexos": True,
            "excepciones": True,
            "costeo": "completo",
            "ia": "completa",
            "soporte": "prioritario",
        },
        "limits": {
            "paquetes": None,
            "recursos": None,
            "usuarios": 10,
        },
        "is_active": True,
    },
    {
        "name": "Marketplace Gratuito",
        "description": "Plan gratuito del Marketplace. 10 productos, 3 ventas/mes, 3 leads/mes.",
        "price": 0.00,
        "currency": "USD",
        "features": {
            "productos": 10,
            "ventas_mes": 3,
            "leads_mes": 3,
            "diagnostico": "genérico",
            "recomendaciones": "fijas",
        },
        "limits": {
            "productos": 10,
            "ventas_mes": 3,
            "leads_mes": 3,
        },
        "is_active": True,
    },
    {
        "name": "Marketplace Básico",
        "description": "Plan básico del Marketplace. 100 productos, 20 ventas/mes, 10 leads/mes.",
        "price": 19.00,
        "currency": "USD",
        "features": {
            "productos": 100,
            "ventas_mes": 20,
            "leads_mes": 10,
            "diagnostico": "específico",
            "recomendaciones": "personalizadas",
            "filtros": True,
            "categorias": True,
        },
        "limits": {
            "productos": 100,
            "ventas_mes": 20,
            "leads_mes": 10,
        },
        "is_active": True,
    },
    {
        "name": "Marketplace Plus",
        "description": "Plan plus del Marketplace. Productos ilimitados, 40 ventas/mes, 30 leads/mes.",
        "price": 35.00,
        "currency": "USD",
        "features": {
            "productos": "ilimitados",
            "ventas_mes": 40,
            "leads_mes": 30,
            "diagnostico": "inteligencia de negocio",
            "recomendaciones": "estratégicas",
            "filtros": True,
            "categorias": True,
            "asistente": True,
        },
        "limits": {
            "productos": None,
            "ventas_mes": 40,
            "leads_mes": 30,
        },
        "is_active": True,
    },
]


def seed_plans(db: Session) -> int:
    """Crea los planes iniciales."""
    count = 0
    for data in PLANS:
        existing = db.query(Plan).filter(Plan.name == data["name"]).first()
        if not existing:
            db.add(Plan(**data))
            count += 1
    db.commit()
    return count