from unittest.mock import MagicMock

import pytest

from resume_screening.db import session


def test_session_factory_uses_configured_engine(monkeypatch) -> None:
    engine = MagicMock()

    monkeypatch.setattr(session, "get_engine", lambda: engine)

    session.get_session_factory.cache_clear()

    try:
        factory = session.get_session_factory()
        database_session = factory()

        assert database_session.bind is engine
        assert database_session.expire_on_commit is False

        database_session.close()
    finally:
        session.get_session_factory.cache_clear()


def test_session_scope_rolls_back_and_closes_on_error(monkeypatch) -> None:
    database_session = MagicMock()

    factory = MagicMock()
    factory.return_value = database_session

    monkeypatch.setattr(
        session,
        "get_session_factory",
        lambda: factory,
    )

    with pytest.raises(RuntimeError, match="test failure"):
        with session.session_scope():
            raise RuntimeError("test failure")

    database_session.rollback.assert_called_once()
    database_session.close.assert_called_once()