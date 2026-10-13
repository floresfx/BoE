"""Seed de paises.

Resuelve timezone_code -> timezone_id y currency_code -> currency_id.
"""

from sqlalchemy.orm import Session

from app.models import Country, Currency, Timezone


COUNTRIES = [
    {"code": "VE", "name": "Venezuela", "timezone_code": "America/Caracas", "currency_code": "VES", "phone_prefix": "+58"},
    {"code": "CO", "name": "Colombia", "timezone_code": "America/Bogota", "currency_code": "COP", "phone_prefix": "+57"},
    {"code": "PA", "name": "Panama", "timezone_code": "America/Panama", "currency_code": "PAB", "phone_prefix": "+507"},
    {"code": "CL", "name": "Chile", "timezone_code": "America/Santiago", "currency_code": "CLP", "phone_prefix": "+56"},
    {"code": "PE", "name": "Peru", "timezone_code": "America/Lima", "currency_code": "PEN", "phone_prefix": "+51"},
    {"code": "EC", "name": "Ecuador", "timezone_code": "America/Guayaquil", "currency_code": "USD", "phone_prefix": "+593"},
    {"code": "MX", "name": "Mexico", "timezone_code": "America/Mexico_City", "currency_code": "MXN", "phone_prefix": "+52"},
    {"code": "AR", "name": "Argentina", "timezone_code": "America/Argentina/Buenos_Aires", "currency_code": "ARS", "phone_prefix": "+54"},
    {"code": "ES", "name": "Espana", "timezone_code": "Europe/Madrid", "currency_code": "EUR", "phone_prefix": "+34"},
    {"code": "US", "name": "Estados Unidos", "timezone_code": "America/New_York", "currency_code": "USD", "phone_prefix": "+1"},
]


def seed_countries(db: Session) -> int:
    """Crea los paises iniciales. Idempotente."""
    count = 0

    timezones = {t.code: t for t in db.query(Timezone).all()}
    currencies = {c.code: c for c in db.query(Currency).all()}

    for data in COUNTRIES:
        existing = (
            db.query(Country).filter(Country.code == data["code"]).first()
        )
        if existing:
            continue

        tz = timezones.get(data["timezone_code"])
        cur = currencies.get(data["currency_code"])

        if not tz or not cur:
            raise ValueError(
                f"No encontrado: tz={data['timezone_code']} cur={data['currency_code']}"
            )

        db.add(
            Country(
                code=data["code"],
                name=data["name"],
                timezone_id=tz.id,
                currency_id=cur.id,
                phone_prefix=data["phone_prefix"],
            )
        )
        count += 1

    db.commit()
    return count