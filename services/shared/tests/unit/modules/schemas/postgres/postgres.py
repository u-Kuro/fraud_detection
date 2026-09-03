from services.shared.src.modules.schemas.postgres.postgres import PostgresTableBase

def test_postgres_table_base_is_declarative_base():
    from sqlalchemy.orm import DeclarativeBase
    assert issubclass(PostgresTableBase, DeclarativeBase)

def test_postgres_table_base_can_be_subclassed():
    from sqlalchemy import Column, Integer

    class MyTable(PostgresTableBase):
        __tablename__ = "my_table_unique_for_test"
        id = Column(Integer, primary_key=True)

    assert issubclass(MyTable, PostgresTableBase)
