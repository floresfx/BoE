"""Seed de impuestos."""

from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Country, Tax


TAXES = [
    ("VE", "IVA", "IVA", "16.00", "general"),
    ("CO", "IVA", "IVA", "19.00", "general"),
    ("PA", "ITBMS", "ITBMS", "7.00", "general"),
    ("CL", "IVA", "IVA", "19.00", "general"),
    ("PE", "IGV", "IGV", "18.00", "general"),
    ("EC", "IVA", "IVA", "12.00", "general"),
    ("MX", "IVA", "IVA", "16.00", "general"),
    ("AR", "IVA", "IVA", "21.00", "general"),
    ("ES", "IVA", "IVA", "21.00", "general"),
    ("US", "SALES_TAX", "Sales Tax", "0.00", "general"),
]


def seed_taxes(db: Session) -> int:
    """Crea los impuestos iniciales. Idempotente."""
    count = 0

    countries = {c.code: c for c in db.query(Country).all()}

    for country_code, code, name, rate, applies_to in TAXES:
        country = countries.get(country_code)
        if not country:
            raise ValueError(f"Pais no encontrado: {country_code}")

        existing = (
            db.query(Tax)
            .filter(
                Tax.country_id == country.id,
                Tax.code == code,
            )
            .first()
        )
        if existing:
            continue

        db.add(
            Tax(
                country_id=country.id,
                code=code,
                name=name,
                rate=Decimal(rate),
                applies_to=applies_to,
            )
        )
        count += 1

    db.commit()
    return count