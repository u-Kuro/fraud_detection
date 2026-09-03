from sqlalchemy.orm import sessionmaker
from services.fraud_detection.src.repositories.postgres.postgres import sql_session

def test_sql_session_is_sessionmaker():
    assert isinstance(sql_session, sessionmaker)
