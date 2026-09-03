from dags.shared.modules.schemas.postgres.postgres import PostgresTableBase

def test_postgres_table_base_is_declarative_base():
    from sqlalchemy.orm import DeclarativeBase
    assert issubclass(PostgresTableBase, DeclarativeBase)
