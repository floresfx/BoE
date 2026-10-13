"""Seed de formatos de número."""

from sqlalchemy.orm import Session

from app.models import NumberFormat


NUMBER_FORMATS = [
    {
        "code": "en_US",
        "thousands_sep": ",",
        "decimal_sep": ".",
        "example": "1,000.00",
    },
    {
        "code": "es_ES",
        "thousands_sep": ".",
        "decimal_sep": ",",
        "example": "1.000,00",
    },
    {
        "code": "fr_FR",
        "thousands_sep": " ",
        "decimal_sep": ",",
        "example": "1 000,00",
    },
]


def seed_number_formats(db: Session) -> int:
    """Crea los formatos de número iniciales. Idempotente."""
    count = 0
    for data in NUMBER_FORMATS:
        existing = (
            db.query(NumberFormat)
            .filter(NumberFormat.code == data["code"])
            .first()
        )
        if not existing:
            db.add(NumberFormat(**data))
            count += 1
    db.commit()
    return count