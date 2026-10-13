"""Seed de atributos.

Resuelve type_code → type_id.
"""

from sqlalchemy.orm import Session

from app.models import Attribute, AttributeType


ATTRIBUTES = [
    {"code": "certificado", "name": "Certificado", "type_code": "boolean"},
    {"code": "esterilizado", "name": "Esterilizado", "type_code": "boolean"},
    {"code": "desechable", "name": "Desechable", "type_code": "boolean"},
    {"code": "reutilizable", "name": "Reutilizable", "type_code": "boolean"},
    {"code": "caducable", "name": "Caducable", "type_code": "boolean"},
    {"code": "refrigerado", "name": "Refrigerado", "type_code": "boolean"},
    {"code": "fresco", "name": "Fresco", "type_code": "boolean"},
    {"code": "congelado", "name": "Congelado", "type_code": "boolean"},
    {"code": "organico", "name": "Orgánico", "type_code": "boolean"},
    {"code": "sin_gluten", "name": "Sin gluten", "type_code": "boolean"},
    {"code": "sin_lactosa", "name": "Sin lactosa", "type_code": "boolean"},
    {"code": "vegano", "name": "Vegano", "type_code": "boolean"},
    {"code": "vegetariano", "name": "Vegetariano", "type_code": "boolean"},
    {"code": "original", "name": "Original", "type_code": "boolean"},
    {"code": "generico", "name": "Genérico", "type_code": "boolean"},
    {"code": "importado", "name": "Importado", "type_code": "boolean"},
    {"code": "nacional", "name": "Nacional", "type_code": "boolean"},
    {"code": "nuevo", "name": "Nuevo", "type_code": "boolean"},
    {"code": "usado", "name": "Usado", "type_code": "boolean"},
    {"code": "reacondicionado", "name": "Reacondicionado", "type_code": "boolean"},
    {"code": "pesado", "name": "Pesado", "type_code": "boolean"},
    {"code": "voluminoso", "name": "Voluminoso", "type_code": "boolean"},
    {"code": "fragil", "name": "Frágil", "type_code": "boolean"},
    {"code": "peligroso", "name": "Peligroso", "type_code": "boolean"},
    {"code": "premium", "name": "Premium", "type_code": "boolean"},
    {"code": "personalizado", "name": "Personalizado", "type_code": "boolean"},
    {"code": "estandar", "name": "Estándar", "type_code": "boolean"},
    {"code": "economico", "name": "Económico", "type_code": "boolean"},
    {"code": "industrial", "name": "Industrial", "type_code": "boolean"},
    {"code": "ecologico", "name": "Ecológico", "type_code": "boolean"},
    {"code": "preventivo", "name": "Preventivo", "type_code": "boolean"},
    {"code": "correctivo", "name": "Correctivo", "type_code": "boolean"},
    {"code": "predictivo", "name": "Predictivo", "type_code": "boolean"},
    {"code": "emergencia", "name": "Emergencia", "type_code": "boolean"},
    {"code": "digital", "name": "Digital", "type_code": "boolean"},
    {"code": "impreso", "name": "Impreso", "type_code": "boolean"},
    {"code": "audiovisual", "name": "Audiovisual", "type_code": "boolean"},
    {"code": "interactivo", "name": "Interactivo", "type_code": "boolean"},
    {"code": "presencial", "name": "Presencial", "type_code": "boolean"},
    {"code": "online", "name": "Online", "type_code": "boolean"},
    {"code": "rustico", "name": "Rústico", "type_code": "boolean"},
    {"code": "al_por_mayor", "name": "Al por mayor", "type_code": "boolean"},
    {"code": "pedido_minimo", "name": "Pedido mínimo", "type_code": "numeric"},
    {"code": "certificacion", "name": "Certificación", "type_code": "boolean"},
]


def seed_attributes(db: Session) -> int:
    """Crea los atributos iniciales. Idempotente."""
    count = 0

    # Cache de tipos por code
    types = {t.code: t for t in db.query(AttributeType).all()}

    if not types:
        raise RuntimeError("No hay attribute_types. Ejecuta seed_attribute_types primero.")

    for data in ATTRIBUTES:
        attr_type = types.get(data["type_code"])
        if not attr_type:
            raise ValueError(f"Tipo no encontrado: {data['type_code']}")

        existing = (
            db.query(Attribute)
            .filter(Attribute.code == data["code"])
            .first()
        )
        if existing:
            continue

        db.add(
            Attribute(
                code=data["code"],
                name=data["name"],
                type_id=attr_type.id,
            )
        )
        count += 1

    db.commit()
    return count