"""Seed de tipos de documento."""

from sqlalchemy.orm import Session

from app.models import Country, DocumentType


DOCUMENT_TYPES = [
    # (code, name, country_code or None, format, regex)
    ("VE_RIF", "RIF", "VE", "J-12345678-9", r"^[JGVEP]-\d{8}-\d$"),
    ("VE_CEDULA", "Cedula", "VE", "V-12345678", r"^[VE]-\d{7,8}$"),
    ("CO_NIT", "NIT", "CO", "900123456-7", r"^\d{9}-\d$"),
    ("CO_CC", "Cedula de ciudadania", "CO", "1234567890", r"^\d{8,10}$"),
    ("PE_RUC", "RUC", "PE", "20123456789", r"^\d{11}$"),
    ("CL_RUT", "RUT", "CL", "12.345.678-9", r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$"),
    ("MX_RFC", "RFC", "MX", "XAXX010101000", r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$"),
    ("ES_NIF", "NIF", "ES", "12345678Z", r"^\d{8}[A-Z]$"),
    ("PASSPORT", "Pasaporte", None, None, None),
    ("US_EIN", "EIN", "US", "12-3456789", r"^\d{2}-\d{7}$"),
]


def seed_document_types(db: Session) -> int:
    """Crea los tipos de documento iniciales. Idempotente."""
    count = 0

    countries = {c.code: c for c in db.query(Country).all()}

    for code, name, country_code, fmt, regex in DOCUMENT_TYPES:
        country = countries.get(country_code) if country_code else None

        existing = (
            db.query(DocumentType)
            .filter(DocumentType.code == code)
            .first()
        )
        if existing:
            continue

        db.add(
            DocumentType(
                code=code,
                name=name,
                country_id=country.id if country else None,
                format=fmt,
                regex=regex,
            )
        )
        count += 1

    db.commit()
    return count