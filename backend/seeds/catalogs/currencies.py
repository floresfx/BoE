"""Seed de monedas."""

from sqlalchemy.orm import Session

from app.models import Currency


CURRENCIES = [
    {
        "code": "USD",
        "name": "Dólar estadounidense",
        "symbol": "$",
        "decimals": 2,
        "is_base": True,
    },
    {
        "code": "VES",
        "name": "Bolívar venezolano",
        "symbol": "Bs.",
        "decimals": 2,
        "is_base": False,
    },
    {
        "code": "EUR",
        "name": "Euro",
        "symbol": "€",
        "decimals": 2,
        "is_base": False,
    },
    {
        "code": "COP",
        "name": "Peso colombiano",
        "symbol": "$",
        "decimals": 0,
        "is_base": False,
    },
    {
        "code": "CLP",
        "name": "Peso chileno",
        "symbol": "$",
        "decimals": 0,
        "is_base": False,
    },
    {
        "code": "PEN",
        "name": "Sol peruano",
        "symbol": "S/",
        "decimals": 2,
        "is_base": False,
    },
    {
        "code": "PAB",
        "name": "Balboa panameño",
        "symbol": "B/.",
        "decimals": 2,
        "is_base": False,
    },
    {
        "code": "MXN",
        "name": "Peso mexicano",
        "symbol": "$",
        "decimals": 2,
        "is_base": False,
    },
    {
        "code": "ARS",
        "name": "Peso argentino",
        "symbol": "$",
        "decimals": 2,
        "is_base": False,
    },
    {
        "code": "USDT",
        "name": "Tether (cripto)",
        "symbol": "₮",
        "decimals": 6,
        "is_base": False,
    },
]


def seed_currencies(db: Session) -> int:
    """Crea las monedas iniciales. Idempotente."""
    count = 0
    for data in CURRENCIES:
        existing = db.query(Currency).filter(Currency.code == data["code"]).first()
        if not existing:
            db.add(Currency(**data))
            count += 1
    db.commit()
    return count