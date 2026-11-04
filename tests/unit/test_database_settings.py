from sqlalchemy.engine import URL

from resume_screening.config.settings import Settings


def test_database_url_is_constructed_from_settings() -> None:
    settings = Settings(
        postgres_db="test_db",
        postgres_user="test_user",
        postgres_password="test_password",
        postgres_host="test_host",
        postgres_port=5433,
    )

    database_url = settings.database_url

    assert isinstance(database_url, URL)
    assert database_url.drivername == "postgresql+psycopg"
    assert database_url.username == "test_user"
    assert database_url.password == "test_password"
    assert database_url.host == "test_host"
    assert database_url.port == 5433
    assert database_url.database == "test_db"