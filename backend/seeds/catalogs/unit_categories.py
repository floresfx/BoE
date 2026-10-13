"""Seed de categorías de unidades."""

from sqlalchemy.orm import Session

from app.models import UnitCategory


UNIT_CATEGORIES = [
    {"code": "peso", "name": "Peso"},
    {"code": "volumen", "name": "Volumen"},
    {"code": "longitud", "name": "Longitud"},
    {"code": "area", "name": "Área"},
    {"code": "unidad", "name": "Unidad"},
    {"code": "empaque", "name": "Empaque"},
    {"code": "tiempo", "name": "Tiempo"},
    {"code": "culinario", "name": "Culinario"},
]


def seed_unit_categories(db: Session) -> int:
    """Crea las categorías de unidades. Idempotente."""
    count = 0
    for data in UNIT_CATEGORIES:
        existing = (
            db.query(UnitCategory)
            .filter(UnitCategory.code == data["code"])
            .first()
        )
        if not existing:
            db.add(UnitCategory(**data))
            count += 1
    db.commit()
    return count