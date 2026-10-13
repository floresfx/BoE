"""Seed de unidades de medida.

Resuelve category_code → category_id al insertar.
"""

from sqlalchemy.orm import Session

from app.models import Unit, UnitCategory


UNITS = [
    # Peso
    {"code": "kg", "name": "Kilogramo", "symbol": "kg", "category_code": "peso", "is_base": True},
    {"code": "g", "name": "Gramo", "symbol": "g", "category_code": "peso", "is_base": False},
    {"code": "mg", "name": "Miligramo", "symbol": "mg", "category_code": "peso", "is_base": False},
    {"code": "lb", "name": "Libra", "symbol": "lb", "category_code": "peso", "is_base": False},
    {"code": "oz", "name": "Onza", "symbol": "oz", "category_code": "peso", "is_base": False},
    {"code": "ton", "name": "Tonelada", "symbol": "t", "category_code": "peso", "is_base": False},
    # Volumen
    {"code": "L", "name": "Litro", "symbol": "L", "category_code": "volumen", "is_base": True},
    {"code": "ml", "name": "Mililitro", "symbol": "ml", "category_code": "volumen", "is_base": False},
    {"code": "gal", "name": "Galón", "symbol": "gal", "category_code": "volumen", "is_base": False},
    {"code": "qt", "name": "Cuarto", "symbol": "qt", "category_code": "volumen", "is_base": False},
    {"code": "pt", "name": "Pinta", "symbol": "pt", "category_code": "volumen", "is_base": False},
    {"code": "fl_oz", "name": "Onza líquida", "symbol": "fl oz", "category_code": "volumen", "is_base": False},
    # Longitud
    {"code": "m", "name": "Metro", "symbol": "m", "category_code": "longitud", "is_base": True},
    {"code": "cm", "name": "Centímetro", "symbol": "cm", "category_code": "longitud", "is_base": False},
    {"code": "mm", "name": "Milímetro", "symbol": "mm", "category_code": "longitud", "is_base": False},
    {"code": "ft", "name": "Pie", "symbol": "ft", "category_code": "longitud", "is_base": False},
    {"code": "in", "name": "Pulgada", "symbol": "in", "category_code": "longitud", "is_base": False},
    {"code": "yd", "name": "Yarda", "symbol": "yd", "category_code": "longitud", "is_base": False},
    {"code": "mi", "name": "Milla", "symbol": "mi", "category_code": "longitud", "is_base": False},
    # Área
    {"code": "m2", "name": "Metro cuadrado", "symbol": "m²", "category_code": "area", "is_base": True},
    {"code": "cm2", "name": "Centímetro cuadrado", "symbol": "cm²", "category_code": "area", "is_base": False},
    {"code": "ft2", "name": "Pie cuadrado", "symbol": "ft²", "category_code": "area", "is_base": False},
    {"code": "in2", "name": "Pulgada cuadrada", "symbol": "in²", "category_code": "area", "is_base": False},
    # Unidad
    {"code": "unidad", "name": "Unidad", "symbol": "u", "category_code": "unidad", "is_base": True},
    {"code": "par", "name": "Par", "symbol": "par", "category_code": "unidad", "is_base": False},
    {"code": "docena", "name": "Docena", "symbol": "doc", "category_code": "unidad", "is_base": False},
    {"code": "ciento", "name": "Ciento", "symbol": "c", "category_code": "unidad", "is_base": False},
    # Empaque
    {"code": "caja", "name": "Caja", "symbol": "caja", "category_code": "empaque", "is_base": True},
    {"code": "paquete", "name": "Paquete", "symbol": "pqt", "category_code": "empaque", "is_base": False},
    {"code": "bolsa", "name": "Bolsa", "symbol": "bolsa", "category_code": "empaque", "is_base": False},
    {"code": "pallet", "name": "Pallet", "symbol": "pallet", "category_code": "empaque", "is_base": False},
    # Tiempo
    {"code": "hora", "name": "Hora", "symbol": "h", "category_code": "tiempo", "is_base": True},
    {"code": "min", "name": "Minuto", "symbol": "min", "category_code": "tiempo", "is_base": False},
    {"code": "dia", "name": "Día", "symbol": "d", "category_code": "tiempo", "is_base": False},
    {"code": "semana", "name": "Semana", "symbol": "sem", "category_code": "tiempo", "is_base": False},
    {"code": "mes", "name": "Mes", "symbol": "mes", "category_code": "tiempo", "is_base": False},
    # Culinario
    {"code": "taza", "name": "Taza", "symbol": "taza", "category_code": "culinario", "is_base": True},
    {"code": "cucharada", "name": "Cucharada", "symbol": "cda", "category_code": "culinario", "is_base": False},
    {"code": "cucharadita", "name": "Cucharadita", "symbol": "cdta", "category_code": "culinario", "is_base": False},
]


def seed_units(db: Session) -> int:
    """Crea las unidades iniciales. Idempotente."""
    count = 0

    # Cache de categorías por code
    categories = {c.code: c for c in db.query(UnitCategory).all()}

    for data in UNITS:
        existing = db.query(Unit).filter(Unit.code == data["code"]).first()
        if existing:
            continue

        category = categories.get(data["category_code"])
        if not category:
            raise ValueError(f"Categoría no encontrada: {data['category_code']}")

        unit = Unit(
            code=data["code"],
            name=data["name"],
            symbol=data["symbol"],
            category_id=category.id,
            is_base=data["is_base"],
        )
        db.add(unit)
        count += 1

    db.commit()
    return count