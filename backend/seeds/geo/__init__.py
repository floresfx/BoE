"""Seeds de geografia y datos fiscales."""

from seeds.geo.cities import seed_cities
from seeds.geo.countries import seed_countries
from seeds.geo.document_types import seed_document_types
from seeds.geo.states import seed_states
from seeds.geo.taxes import seed_taxes

__all__ = [
    "seed_cities",
    "seed_countries",
    "seed_document_types",
    "seed_states",
    "seed_taxes",
]