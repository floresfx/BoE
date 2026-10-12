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
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Sesión de BD para la request.

    NO aplica search_path aquí. Eso lo hace get_current_tenant,
    que es quien conoce el schema. Esta sesión es la MISMA que
    usará get_current_tenant (FastAPI cachea la dependencia).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()