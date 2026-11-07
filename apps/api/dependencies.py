from collections.abc import Iterator

from sqlalchemy.orm import Session

from resume_screening.db.session import session_scope


def get_db_session() -> Iterator[Session]:
    with session_scope() as session:
        yield session
