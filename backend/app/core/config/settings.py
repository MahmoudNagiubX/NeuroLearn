from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


BACKEND_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    APP_NAME: str = "NeuroLearn API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "0.1.0"

    # Optional full override. If missing, DB_* fields are required.
    DATABASE_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None

    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=(BACKEND_ROOT / ".env", BACKEND_ROOT / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_flag(cls, value: object) -> object:
        # Some host environments export DEBUG=release/production; treat these as false.
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value

    @model_validator(mode="after")
    def validate_database_settings(self) -> "Settings":
        if self.DATABASE_URL:
            self.DATABASE_URL = self.DATABASE_URL.strip()
            try:
                make_url(self.DATABASE_URL)
            except Exception as exc:  # noqa: BLE001
                raise ValueError("DATABASE_URL is invalid.") from exc
            return self

        required = {
            "DB_HOST": self.DB_HOST,
            "DB_PORT": self.DB_PORT,
            "DB_NAME": self.DB_NAME,
            "DB_USER": self.DB_USER,
            "DB_PASSWORD": self.DB_PASSWORD,
        }
        missing = [name for name, value in required.items() if value is None or str(value).strip() == ""]
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(
                "Database configuration is incomplete. "
                "Set DATABASE_URL or all DB_* variables. "
                f"Missing: {missing_list}."
            )

        self.DATABASE_URL = URL.create(
            "postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        ).render_as_string(hide_password=False)
        return self

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL is None:
            raise RuntimeError("DATABASE_URL is not configured.")
        return self.DATABASE_URL

    @property
    def sanitized_db_target(self) -> dict[str, Any]:
        parsed = make_url(self.database_url)
        return {
            "host": parsed.host,
            "port": parsed.port,
            "database": parsed.database,
            "username": parsed.username,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
