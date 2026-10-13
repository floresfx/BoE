"""Seed de zonas horarias."""

from sqlalchemy.orm import Session

from app.models import Timezone


TIMEZONES = [
    {"code": "America/Caracas", "friendly_name": "Venezuela", "utc_offset": "UTC-4"},
    {"code": "America/Bogota", "friendly_name": "Colombia", "utc_offset": "UTC-5"},
    {"code": "America/Panama", "friendly_name": "Panamá", "utc_offset": "UTC-5"},
    {"code": "America/Santiago", "friendly_name": "Chile", "utc_offset": "UTC-3/UTC-4"},
    {"code": "America/Lima", "friendly_name": "Perú", "utc_offset": "UTC-5"},
    {"code": "America/Guayaquil", "friendly_name": "Ecuador", "utc_offset": "UTC-5"},
    {"code": "America/Mexico_City", "friendly_name": "México", "utc_offset": "UTC-6/UTC-5"},
    {
        "code": "America/Argentina/Buenos_Aires",
        "friendly_name": "Argentina",
        "utc_offset": "UTC-3",
    },
    {"code": "Europe/Madrid", "friendly_name": "España", "utc_offset": "UTC+1/UTC+2"},
    {
        "code": "America/New_York",
        "friendly_name": "Estados Unidos (Este)",
        "utc_offset": "UTC-5/UTC-4",
    },
]


def seed_timezones(db: Session) -> int:
    """Crea las zonas horarias iniciales. Idempotente."""
    count = 0
    for data in TIMEZONES:
        existing = (
            db.query(Timezone).filter(Timezone.code == data["code"]).first()
        )
        if not existing:
            db.add(Timezone(**data))
            count += 1
    db.commit()
    return count