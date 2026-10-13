"""Seeds de catálogos simples."""

from seeds.catalogs.currencies import seed_currencies
from seeds.catalogs.timezones import seed_timezones
from seeds.catalogs.date_formats import seed_date_formats
from seeds.catalogs.number_formats import seed_number_formats
from seeds.catalogs.attribute_types import seed_attribute_types

__all__ = [
    "seed_currencies",
    "seed_timezones",
    "seed_date_formats",
    "seed_number_formats",
    "seed_attribute_types",
]