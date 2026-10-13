"""Seed de la relación vertical ↔ atributo.

Resuelve vertical_code y attribute_code → UUIDs.
"""

from sqlalchemy.orm import Session

from app.models import Attribute, Vertical, VerticalAttribute


VERTICALS_ATTRIBUTES = [
    # Clínicas generales
    ("clinicas_generales", "certificado", 1),
    ("clinicas_generales", "esterilizado", 2),
    ("clinicas_generales", "desechable", 3),
    ("clinicas_generales", "reutilizable", 4),
    ("clinicas_generales", "caducable", 5),
    ("clinicas_generales", "emergencia", 6),
    # Clínicas dentales
    ("clinicas_dentales", "certificado", 1),
    ("clinicas_dentales", "esterilizado", 2),
    ("clinicas_dentales", "desechable", 3),
    ("clinicas_dentales", "reutilizable", 4),
    ("clinicas_dentales", "caducable", 5),
    # Panaderías
    ("panaderias", "fresco", 1),
    ("panaderias", "congelado", 2),
    ("panaderias", "organico", 3),
    ("panaderias", "sin_gluten", 4),
    ("panaderias", "sin_lactosa", 5),
    ("panaderias", "caducable", 6),
    # Restaurantes
    ("restaurantes", "fresco", 1),
    ("restaurantes", "congelado", 2),
    ("restaurantes", "organico", 3),
    ("restaurantes", "sin_gluten", 4),
    ("restaurantes", "vegetariano", 5),
    ("restaurantes", "caducable", 6),
    # Fabricantes
    ("fabricantes", "original", 1),
    ("fabricantes", "generico", 2),
    ("fabricantes", "importado", 3),
    ("fabricantes", "nacional", 4),
    ("fabricantes", "pesado", 5),
    # Instituciones educativas
    ("instituciones_educativas", "digital", 1),
    ("instituciones_educativas", "impreso", 2),
    ("instituciones_educativas", "audiovisual", 3),
    ("instituciones_educativas", "interactivo", 4),
    ("instituciones_educativas", "presencial", 5),
    ("instituciones_educativas", "online", 6),
    # Proyectos por encargo
    ("proyectos_por_encargo", "personalizado", 1),
    ("proyectos_por_encargo", "estandar", 2),
    ("proyectos_por_encargo", "premium", 3),
    ("proyectos_por_encargo", "economico", 4),
    # Empresas de limpieza
    ("empresas_limpieza", "desechable", 1),
    ("empresas_limpieza", "reutilizable", 2),
    ("empresas_limpieza", "ecologico", 3),
    ("empresas_limpieza", "industrial", 4),
    # Empresas de mantenimiento
    ("empresas_mantenimiento", "preventivo", 1),
    ("empresas_mantenimiento", "correctivo", 2),
    ("empresas_mantenimiento", "predictivo", 3),
    ("empresas_mantenimiento", "emergencia", 4),
    # Empresas de transporte
    ("empresas_transporte", "refrigerado", 1),
    ("empresas_transporte", "peligroso", 2),
    ("empresas_transporte", "fragil", 3),
    ("empresas_transporte", "pesado", 4),
    ("empresas_transporte", "voluminoso", 5),
    # Hoteles
    ("hoteles", "nuevo", 1),
    ("hoteles", "usado", 2),
    ("hoteles", "desechable", 3),
    ("hoteles", "reutilizable", 4),
    ("hoteles", "premium", 5),
    # Heladerías
    ("heladerias", "fresco", 1),
    ("heladerias", "congelado", 2),
    ("heladerias", "organico", 3),
    ("heladerias", "sin_lactosa", 4),
    ("heladerias", "vegano", 5),
    # Talleres
    ("talleres", "original", 1),
    ("talleres", "generico", 2),
    ("talleres", "nuevo", 3),
    ("talleres", "usado", 4),
    ("talleres", "reacondicionado", 5),
    # Ferreterías
    ("ferreterias", "original", 1),
    ("ferreterias", "generico", 2),
    ("ferreterias", "nuevo", 3),
    ("ferreterias", "usado", 4),
    ("ferreterias", "importado", 5),
    # Distribuidoras
    ("distribuidoras", "original", 1),
    ("distribuidoras", "generico", 2),
    ("distribuidoras", "importado", 3),
    ("distribuidoras", "nacional", 4),
    ("distribuidoras", "al_por_mayor", 5),
    ("distribuidoras", "pedido_minimo", 6),
    # Laboratorios
    ("laboratorios", "certificado", 1),
    ("laboratorios", "esterilizado", 2),
    ("laboratorios", "desechable", 3),
    ("laboratorios", "caducable", 4),
    ("laboratorios", "refrigerado", 5),
    ("laboratorios", "certificacion", 6),
    # Academias
    ("academias", "digital", 1),
    ("academias", "impreso", 2),
    ("academias", "audiovisual", 3),
    ("academias", "presencial", 4),
    ("academias", "online", 5),
    # Construcción
    ("construccion", "original", 1),
    ("construccion", "generico", 2),
    ("construccion", "pesado", 3),
    ("construccion", "importado", 4),
    ("construccion", "industrial", 5),
    # Diseño
    ("diseño", "personalizado", 1),
    ("diseño", "estandar", 2),
    ("diseño", "premium", 3),
    ("diseño", "digital", 4),
    ("diseño", "impreso", 5),
]


def seed_verticals_attributes(db: Session) -> int:
    """Crea la relación vertical ↔ atributo. Idempotente."""
    count = 0

    verticals = {v.code: v for v in db.query(Vertical).all()}
    attributes = {a.code: a for a in db.query(Attribute).all()}

    for vertical_code, attr_code, order in VERTICALS_ATTRIBUTES:
        vertical = verticals.get(vertical_code)
        attribute = attributes.get(attr_code)

        if not vertical or not attribute:
            raise ValueError(
                f"No encontrado: {vertical_code} ↔ {attr_code}"
            )

        existing = (
            db.query(VerticalAttribute)
            .filter(
                VerticalAttribute.vertical_id == vertical.id,
                VerticalAttribute.attribute_id == attribute.id,
            )
            .first()
        )
        if existing:
            continue

        db.add(
            VerticalAttribute(
                vertical_id=vertical.id,
                attribute_id=attribute.id,
                is_required=False,
                display_order=order,
            )
        )
        count += 1

    db.commit()
    return count