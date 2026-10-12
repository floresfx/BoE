from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Base de datos
    DATABASE_URL: str = (
        "postgresql+psycopg://boe_user:boe_password@localhost:5432/boe_dev"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "BoE_Mpr"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # CORS: CSV desde .env ("a,b") o JSON (["a","b"])
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Devuelve CORS_ORIGINS como lista.

        Acepta:
        - CSV:  "http://a.com,http://b.com"
        - JSON: '["http://a.com","http://b.com"]'
        """
        v = self.CORS_ORIGINS.strip()
        if not v:
            return []
        if v.startswith("["):
            import json
            return json.loads(v)
        return [item.strip() for item in v.split(",") if item.strip()]


settings = Settings()