from sqlalchemy import inspect, text

from epicevent.infrastructure.base import Base, engine as prod_engine


def test_database_connection_is_active():
    with prod_engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        assert "PostgreSQL" in result.one()[0]


def test_test_database_connection_is_active(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        assert "PostgreSQL" in result.one()[0]


def test_database_schema_matches_metadata(engine):
    inspector = inspect(engine)

    metadata_tables = set(Base.metadata.tables.keys())
    database_tables = set(inspector.get_table_names())

    assert metadata_tables
    assert database_tables == metadata_tables
