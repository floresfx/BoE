"""Seed de conversiones de unidades.

Resuelve from_unit_code y to_unit_code → UUIDs.
"""

from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Unit, UnitConversion


CONVERSIONS = [
    # Peso
    {"from": "kg", "to": "g", "factor": "1000"},
    {"from": "kg", "to": "lb", "factor": "2.20462"},
    {"from": "kg", "to": "oz", "factor": "35.274"},
    {"from": "g", "to": "mg", "factor": "1000"},
    {"from": "ton", "to": "kg", "factor": "1000"},
    {"from": "lb", "to": "oz", "factor": "16"},
    # Volumen
    {"from": "L", "to": "ml", "factor": "1000"},
    {"from": "L", "to": "gal", "factor": "0.264172"},
    {"from": "L", "to": "qt", "factor": "1.05669"},
    {"from": "L", "to": "pt", "factor": "2.11338"},
    {"from": "L", "to": "fl_oz", "factor": "33.814"},
    {"from": "gal", "to": "qt", "factor": "4"},
    {"from": "qt", "to": "pt", "factor": "2"},
    {"from": "pt", "to": "fl_oz", "factor": "16"},
    # Longitud
    {"from": "m", "to": "cm", "factor": "100"},
    {"from": "m", "to": "mm", "factor": "1000"},
    {"from": "m", "to": "ft", "factor": "3.28084"},
    {"from": "m", "to": "in", "factor": "39.3701"},
    {"from": "m", "to": "yd", "factor": "1.09361"},
    {"from": "cm", "to": "mm", "factor": "10"},
    {"from": "ft", "to": "in", "factor": "12"},
    {"from": "yd", "to": "ft", "factor": "3"},
    {"from": "mi", "to": "m", "factor": "1609.34"},
    # Área
    {"from": "m2", "to": "cm2", "factor": "10000"},
    {"from": "m2", "to": "ft2", "factor": "10.7639"},
    {"from": "ft2", "to": "in2", "factor": "144"},
    # Unidad
    {"from": "docena", "to": "unidad", "factor": "12"},
    {"from": "ciento", "to": "unidad", "factor": "100"},
    {"from": "par", "to": "unidad", "factor": "2"},
    # Culinario
    {"from": "taza", "to": "ml", "factor": "240"},
    {"from": "cucharada", "to": "ml", "factor": "15"},
    {"from": "cucharadita", "to": "ml", "factor": "5"},
    {"from": "cucharada", "to": "cucharadita", "factor": "3"},
    # Tiempo
    {"from": "dia", "to": "hora", "factor": "24"},
    {"from": "hora", "to": "min", "factor": "60"},
    {"from": "semana", "to": "dia", "factor": "7"},
    {"from": "mes", "to": "dia", "factor": "30"},
]


def seed_unit_conversions(db: Session) -> int:
    """Crea las conversiones de unidades. Idempotente."""
    count = 0

    # Cache de units por code
    units = {u.code: u for u in db.query(Unit).all()}

    for data in CONVERSIONS:
        from_unit = units.get(data["from"])
        to_unit = units.get(data["to"])

        if not from_unit or not to_unit:
            raise ValueError(
                f"Unidad no encontrada: {data['from']} → {data['to']}"
            )

        existing = (
            db.query(UnitConversion)
            .filter(
                UnitConversion.from_unit_id == from_unit.id,
                UnitConversion.to_unit_id == to_unit.id,
            )
            .first()
        )
        if existing:
            continue

        conversion = UnitConversion(
            from_unit_id=from_unit.id,
            to_unit_id=to_unit.id,
            factor=Decimal(data["factor"]),
            is_base=True,
        )
        db.add(conversion)
        count += 1

    db.commit()
    return count