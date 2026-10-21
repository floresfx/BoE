"""Endpoints de solo lectura para catálogos globales.

Estos endpoints exponen los datos maestros (units, categories, etc.)
al frontend para que pueda poblar los selects.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Attribute,
    Category,
    Country,
    Subcategory,
    Tax,
    Unit,
    UnitCategory,
)

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


@router.get("/units")
def list_units(db: Session = Depends(get_db)):
    """Lista todas las unidades activas."""
    units = (
        db.query(Unit)
        .filter(Unit.is_active.is_(True))
        .order_by(Unit.name)
        .all()
    )
    return [
        {
            "id": str(u.id),
            "code": u.code,
            "name": u.name,
            "symbol": u.symbol,
            "category_id": str(u.category_id),
            "is_base": u.is_base,
        }
        for u in units
    ]


@router.get("/unit-categories")
def list_unit_categories(db: Session = Depends(get_db)):
    """Lista todas las categorías de unidades."""
    cats = (
        db.query(UnitCategory)
        .filter(UnitCategory.is_active.is_(True))
        .order_by(UnitCategory.name)
        .all()
    )
    return [
        {"id": str(c.id), "code": c.code, "name": c.name} for c in cats
    ]


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """Lista todas las categorías activas."""
    cats = (
        db.query(Category)
        .filter(Category.is_active.is_(True))
        .order_by(Category.name)
        .all()
    )
    return [
        {"id": str(c.id), "code": c.code, "name": c.name} for c in cats
    ]


@router.get("/subcategories")
def list_subcategories(
    category_id: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Lista subcategorías, opcionalmente filtradas por categoría."""
    query = db.query(Subcategory).filter(Subcategory.is_active.is_(True))
    if category_id:
        query = query.filter(Subcategory.category_id == category_id)
    subs = query.order_by(Subcategory.name).all()
    return [
        {
            "id": str(s.id),
            "category_id": str(s.category_id),
            "code": s.code,
            "name": s.name,
        }
        for s in subs
    ]


@router.get("/attributes")
def list_attributes(db: Session = Depends(get_db)):
    """Lista todos los atributos activos."""
    attrs = (
        db.query(Attribute)
        .filter(Attribute.is_active.is_(True))
        .order_by(Attribute.name)
        .all()
    )
    return [
        {
            "id": str(a.id),
            "code": a.code,
            "name": a.name,
            "type_id": str(a.type_id),
        }
        for a in attrs
    ]


@router.get("/taxes")
def list_taxes(db: Session = Depends(get_db)):
    """Lista todos los impuestos activos."""
    taxes = (
        db.query(Tax).filter(Tax.is_active.is_(True)).order_by(Tax.name).all()
    )
    return [
        {
            "id": str(t.id),
            "country_id": str(t.country_id),
            "code": t.code,
            "name": t.name,
            "rate": str(t.rate),
            "applies_to": t.applies_to,
        }
        for t in taxes
    ]


@router.get("/countries")
def list_countries(db: Session = Depends(get_db)):
    """Lista todos los países activos."""
    countries = (
        db.query(Country)
        .filter(Country.is_active.is_(True))
        .order_by(Country.name)
        .all()
    )
    return [
        {"code": c.code, "name": c.name, "phone_prefix": c.phone_prefix}
        for c in countries
    ]

@router.get("/currencies")
def list_currencies(db: Session = Depends(get_db)):
    """Lista todas las monedas activas."""
    from app.models import Currency
    currencies = (
        db.query(Currency)
        .filter(Currency.is_active.is_(True))
        .order_by(Currency.code)
        .all()
    )
    return [
        {
            "id": str(c.id),
            "code": c.code,
            "name": c.name,
            "symbol": c.symbol,
        }
        for c in currencies
    ]

from app.models import DateFormat, NumberFormat  # <--- Añadir a las importaciones

# ... (al final del archivo, junto a los demás)

@router.get("/date-formats")
def list_date_formats(db: Session = Depends(get_db)):
    """Lista todos los formatos de fecha activos."""
    formats = (
        db.query(DateFormat)
        .filter(DateFormat.is_active.is_(True))
        .order_by(DateFormat.code)
        .all()
    )
    return [
        {
            "id": str(f.id),
            "code": f.code,
            "example": f.example,
        }
        for f in formats
    ]


@router.get("/number-formats")
def list_number_formats(db: Session = Depends(get_db)):
    """Lista todos los formatos de número activos."""
    formats = (
        db.query(NumberFormat)
        .filter(NumberFormat.is_active.is_(True))
        .order_by(NumberFormat.code)
        .all()
    )
    return [
        {
            "id": str(f.id),
            "code": f.code,
            "example": f.example,
        }
        for f in formats
    ]