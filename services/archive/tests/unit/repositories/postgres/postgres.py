from sqlalchemy.orm import sessionmaker

from services.archive.src.repositories.postgres.postgres import sql_session

def test_sql_session_is_sessionmaker():
    assert isinstance(sql_session, sessionmaker)

def test_sql_session_is_not_none():
    assert sql_session is not None
