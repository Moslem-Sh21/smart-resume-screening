from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_name: str = "Smart Resume Screening"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = Field(default=8000, ge=1, le=65535)
    postgres_db: str = "smart_resume_screening"
    postgres_user: str = "resume_user"
    postgres_password: str = "change_me"
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)


    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    max_upload_size_mb: int = Field(default=10, ge=1, le=100)
    allowed_file_types: str = "pdf,docx"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def allowed_file_extensions(self) -> set[str]:
        return {
            extension.strip().lower()
            for extension in self.allowed_file_types.split(",")
            if extension.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()

