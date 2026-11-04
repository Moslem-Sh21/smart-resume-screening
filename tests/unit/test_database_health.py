from unittest.mock import MagicMock

from resume_screening.db import health


def test_check_database_connection_returns_true(monkeypatch) -> None:
    result = MagicMock()
    result.scalar_one.return_value = 1

    connection = MagicMock()
    connection.execute.return_value = result

    connection_context = MagicMock()
    connection_context.__enter__.return_value = connection

    engine = MagicMock()
    engine.connect.return_value = connection_context

    monkeypatch.setattr(health, "get_engine", lambda: engine)

    assert health.check_database_connection() is True