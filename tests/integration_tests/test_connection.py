from sqlalchemy import text

from src.epicevent.database import engine


def test_database_connection_is_active():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        assert "PostgreSQL" in result.one()[0]
