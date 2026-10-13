"""Seed de tipos de atributo."""

from sqlalchemy.orm import Session

from app.models import AttributeType


ATTRIBUTE_TYPES = [
    {"code": "boolean", "name": "Booleano"},
    {"code": "numeric", "name": "Numérico"},
    {"code": "text", "name": "Texto"},
    {"code": "list", "name": "Lista"},
]


def seed_attribute_types(db: Session) -> int:
    """Crea los tipos de atributo iniciales. Idempotente."""
    count = 0
    for data in ATTRIBUTE_TYPES:
        existing = (
            db.query(AttributeType)
            .filter(AttributeType.code == data["code"])
            .first()
        )
        if not existing:
            db.add(AttributeType(**data))
            count += 1
    db.commit()
    return count