"""Seeds de catálogos."""

# Bloque 1
from seeds.catalogs.attribute_types import seed_attribute_types
from seeds.catalogs.currencies import seed_currencies
from seeds.catalogs.date_formats import seed_date_formats
from seeds.catalogs.number_formats import seed_number_formats
from seeds.catalogs.timezones import seed_timezones

# Bloque 2
from seeds.catalogs.attributes import seed_attributes
from seeds.catalogs.categories import seed_categories
from seeds.catalogs.subcategories import seed_subcategories
from seeds.catalogs.unit_categories import seed_unit_categories
from seeds.catalogs.unit_conversions import seed_unit_conversions
from seeds.catalogs.units import seed_units
from seeds.catalogs.verticals_attributes import seed_verticals_attributes

from seeds.catalogs.features import seed_features
from seeds.catalogs.feature_dependencies import seed_feature_dependencies

__all__ = [
    # Bloque 1
    "seed_attribute_types",
    "seed_currencies",
    "seed_date_formats",
    "seed_number_formats",
    "seed_timezones",
    # Bloque 2
    "seed_attributes",
    "seed_categories",
    "seed_subcategories",
    "seed_unit_categories",
    "seed_unit_conversions",
    "seed_units",
    "seed_verticals_attributes",
    "seed_features",
    "seed_feature_dependencies",
]