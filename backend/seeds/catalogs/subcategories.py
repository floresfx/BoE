"""Seed de subcategorías.

Resuelve category_code → category_id.
"""

from sqlalchemy.orm import Session

from app.models import Category, Subcategory


SUBCATEGORIES = [
    # Salud
    {"category_code": "salud", "code": "material_medico", "name": "Material médico"},
    {"category_code": "salud", "code": "medicamentos", "name": "Medicamentos"},
    {"category_code": "salud", "code": "equipos", "name": "Equipos"},
    {"category_code": "salud", "code": "servicios_salud", "name": "Servicios"},
    # Comida
    {"category_code": "comida", "code": "ingredientes", "name": "Ingredientes"},
    {"category_code": "comida", "code": "comida_preparada", "name": "Comida preparada"},
    {"category_code": "comida", "code": "bebidas", "name": "Bebidas"},
    {"category_code": "comida", "code": "alimentos_secos", "name": "Alimentos secos"},
    # Servicios
    {"category_code": "servicios", "code": "limpieza", "name": "Limpieza"},
    {"category_code": "servicios", "code": "mantenimiento", "name": "Mantenimiento"},
    {"category_code": "servicios", "code": "reparaciones", "name": "Reparaciones"},
    {"category_code": "servicios", "code": "transporte_serv", "name": "Transporte"},
    # Hogar
    {"category_code": "hogar", "code": "muebles", "name": "Muebles"},
    {"category_code": "hogar", "code": "decoracion", "name": "Decoración"},
    {"category_code": "hogar", "code": "electrodomesticos", "name": "Electrodomésticos"},
    {"category_code": "hogar", "code": "jardin", "name": "Jardín"},
    # Construcción
    {"category_code": "construccion", "code": "materiales", "name": "Materiales"},
    {"category_code": "construccion", "code": "herramientas", "name": "Herramientas"},
    {"category_code": "construccion", "code": "pintura", "name": "Pintura"},
    {"category_code": "construccion", "code": "plomeria", "name": "Plomería"},
    # Ropa
    {"category_code": "ropa", "code": "textiles", "name": "Textiles"},
    {"category_code": "ropa", "code": "uniformes", "name": "Uniformes"},
    {"category_code": "ropa", "code": "calzado", "name": "Calzado"},
    {"category_code": "ropa", "code": "accesorios", "name": "Accesorios"},
    # Tecnología
    {"category_code": "tecnologia", "code": "equipos_tec", "name": "Equipos"},
    {"category_code": "tecnologia", "code": "accesorios_tec", "name": "Accesorios"},
    {"category_code": "tecnologia", "code": "software", "name": "Software"},
    {"category_code": "tecnologia", "code": "soporte", "name": "Soporte"},
    # Educación
    {"category_code": "educacion", "code": "cursos", "name": "Cursos"},
    {"category_code": "educacion", "code": "materiales_edu", "name": "Materiales"},
    {"category_code": "educacion", "code": "libros", "name": "Libros"},
    {"category_code": "educacion", "code": "tutorias", "name": "Tutorías"},
    # Transporte
    {"category_code": "transporte", "code": "vehiculos", "name": "Vehículos"},
    {"category_code": "transporte", "code": "repuestos", "name": "Repuestos"},
    {"category_code": "transporte", "code": "servicios_trans", "name": "Servicios"},
    {"category_code": "transporte", "code": "logistica", "name": "Logística"},
    # Otros
    {"category_code": "otros", "code": "general", "name": "General"},
]


def seed_subcategories(db: Session) -> int:
    """Crea las subcategorías. Idempotente."""
    count = 0

    categories = {c.code: c for c in db.query(Category).all()}

    for data in SUBCATEGORIES:
        category = categories.get(data["category_code"])
        if not category:
            raise ValueError(
                f"Categoría no encontrada: {data['category_code']}"
            )

        existing = (
            db.query(Subcategory)
            .filter(
                Subcategory.category_id == category.id,
                Subcategory.code == data["code"],
            )
            .first()
        )
        if existing:
            continue

        db.add(
            Subcategory(
                category_id=category.id,
                code=data["code"],
                name=data["name"],
            )
        )
        count += 1

    db.commit()
    return count