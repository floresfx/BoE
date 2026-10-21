"""Manejador global de errores para FastAPI."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Captura IntegrityError y devuelve un mensaje amigable."""
    
    error_str = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    message = "Error de integridad en la base de datos."
    
    # Traducir errores comunes de PostgreSQL a mensajes legibles
    if "duplicate key value violates unique constraint" in error_str:
        message = "Ya existe un registro con esos datos. Verifica los campos únicos (ej. código, email, RIF)."
    elif "violates foreign key constraint" in error_str:
        message = "El registro está vinculado a otros datos y no se puede modificar o eliminar."
    elif "not-null constraint" in error_str:
        message = "Faltan campos obligatorios por completar."

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": message},
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Captura errores genéricos de SQLAlchemy."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno de base de datos. Contacta a soporte."},
    )