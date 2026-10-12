from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,   # ← NUEVO: no expira atributos tras commit
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Sesión de BD para la request.

    Commit automático al final del request si todo fue bien.
    Rollback si hay excepción.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()          # ← NUEVO: commit automático
    except Exception:
        db.rollback()        # ← NUEVO: rollback si hay error
        raise
    finally:
        db.close()