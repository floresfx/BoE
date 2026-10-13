"""Catálogos globales del sistema."""

# Bloque 1 — Catálogos simples
from app.models.catalogs.attribute_type import AttributeType
from app.models.catalogs.currency import Currency
from app.models.catalogs.date_format import DateFormat
from app.models.catalogs.number_format import NumberFormat
from app.models.catalogs.timezone import Timezone

# Bloque 2 — Catálogos dependientes
from app.models.catalogs.attribute import Attribute
from app.models.catalogs.category import Category
from app.models.catalogs.subcategory import Subcategory
from app.models.catalogs.unit import Unit
from app.models.catalogs.unit_category import UnitCategory
from app.models.catalogs.unit_conversion import UnitConversion
from app.models.catalogs.vertical_attribute import VerticalAttribute

# Bloque 3 — Features
from app.models.catalogs.feature import Feature
from app.models.catalogs.feature_dependency import FeatureDependency

__all__ = [
    # Bloque 1
    "AttributeType",
    "Currency",
    "DateFormat",
    "NumberFormat",
    "Timezone",
    # Bloque 2
    "Attribute",
    "Category",
    "Subcategory",
    "Unit",
    "UnitCategory",
    "UnitConversion",
    "VerticalAttribute",
     # Bloque 3
    "Feature",
    "FeatureDependency",
]