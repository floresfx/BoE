"""Seed de formatos de fecha."""

from sqlalchemy.orm import Session

from app.models import DateFormat


DATE_FORMATS = [
    {"code": "dd/mm/yyyy", "pattern": "Día/Mes/Año", "example": "28/09/2026"},
    {"code": "mm/dd/yyyy", "pattern": "Mes/Día/Año", "example": "09/28/2026"},
    {"code": "yyyy-mm-dd", "pattern": "ISO 8601", "example": "2026-09-28"},
]


def seed_date_formats(db: Session) -> int:
    """Crea los formatos de fecha iniciales. Idempotente."""
    count = 0
    for data in DATE_FORMATS:
        existing = (
            db.query(DateFormat).filter(DateFormat.code == data["code"]).first()
        )
        if not existing:
            db.add(DateFormat(**data))
            count += 1
    db.commit()
    return count