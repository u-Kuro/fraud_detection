from dags.shared.repositories.postgres.postgres import sql_session

def test_sql_session_is_not_none():
    assert sql_session is not None

def test_sql_session_is_sessionmaker():
    from sqlalchemy.orm import sessionmaker
    assert isinstance(sql_session, sessionmaker)
