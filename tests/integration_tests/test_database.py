from sqlalchemy import inspect, text

from epicevents.infrastructure.base import Base


def test_database_connection_is_active(engine):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def test_database_tables_match_metadata(engine):
    inspector = inspect(engine)

    metadata_tables = set(Base.metadata.tables.keys())
    database_tables = set(inspector.get_table_names())

    assert metadata_tables
    assert database_tables == metadata_tables
