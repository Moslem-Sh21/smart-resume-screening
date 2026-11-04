from functools import lru_cache

from sqlalchemy import Engine, create_engine

from resume_screening.config.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )