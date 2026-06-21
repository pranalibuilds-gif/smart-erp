from typing import Literal
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # App Settings
    PROJECT_NAME: str = "Smart ERP"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    APP_DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Workflow Settings
    REORDER_ALERTS_ENABLED: bool = True

    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info) -> str:
        if isinstance(v, str):
            return v

        # Pull required components from data
        data = info.data
        user = data.get("POSTGRES_USER")
        password = data.get("POSTGRES_PASSWORD")
        server = data.get("POSTGRES_SERVER")
        db = data.get("POSTGRES_DB")

        # Assemble the DSN
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=user,
                password=password,
                host=server,
                path=db or "",
            )
        )

    # Security Settings
    # These MUST be provided in environment for production
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
