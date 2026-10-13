"""Seed de categorías (áreas)."""

from sqlalchemy.orm import Session

from app.models import Category


CATEGORIES = [
    {"code": "salud", "name": "Salud"},
    {"code": "comida", "name": "Comida"},
    {"code": "servicios", "name": "Servicios"},
    {"code": "hogar", "name": "Hogar"},
    {"code": "construccion", "name": "Construcción"},
    {"code": "ropa", "name": "Ropa"},
    {"code": "tecnologia", "name": "Tecnología"},
    {"code": "educacion", "name": "Educación"},
    {"code": "transporte", "name": "Transporte"},
    {"code": "otros", "name": "Otros"},
]


def seed_categories(db: Session) -> int:
    """Crea las categorías iniciales. Idempotente."""
    count = 0
    for data in CATEGORIES:
        existing = (
            db.query(Category).filter(Category.code == data["code"]).first()
        )
        if not existing:
            db.add(Category(**data))
            count += 1
    db.commit()
    return count