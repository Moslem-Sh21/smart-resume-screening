from sqlalchemy import text

from resume_screening.db.engine import get_engine


def check_database_connection() -> bool:
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar_one() == 1